package boundless.net.http;

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.util.EntityUtils;

import com.google.common.net.HttpHeaders;
import com.netflix.hystrix.HystrixCommand;
import com.netflix.hystrix.HystrixCommandGroupKey;

import boundless.exception.ErrorCodeException;
import boundless.spring.brave.BraveHelper;
import boundless.utility.IPUtility;
import boundless.utility.JsonUtility;
import boundless.utility.StringUtility;

public class HttpUriRequestHystrixCommand extends HystrixCommand<String> {
	private String user;
	private String password;
	private HttpUriRequest request;
	private Map<String, String> headers;
	private Map<String, String> respHeaders;
	private String contenttype;
	private int timeoutMS;
	private HttpStatusCode status;
	private SSLConnectionSocketFactory sslFactory;

	public HttpUriRequestHystrixCommand(String user, String password, HttpUriRequest request,
			Map<String, String> headers, String contenttype, int timeoutMS, HttpStatusCode status, SSLConnectionSocketFactory sslFactory){
		
		super(HystrixCommandGroupKey.Factory.asKey(request.getURI().toString()));
		
		this.user = user;
		this.password = password;
		this.request = request;
		this.headers = headers;
		this.contenttype = contenttype;
		this.timeoutMS = timeoutMS;
		this.status = status;
		this.sslFactory = sslFactory;
	}
	
	public HttpUriRequestHystrixCommand(String user, String password, HttpUriRequest request,
			Map<String, String> headers, String contenttype, int timeoutMS, HttpStatusCode status, Map<String, String> respHeaders,
			SSLConnectionSocketFactory sslFactory) {
		this(user, password, request, headers, contenttype, timeoutMS, status, sslFactory);
		this.respHeaders = respHeaders;
	}
	

	@Override
	protected String run() throws Exception {
		return doCmd(user, password, request, headers, contenttype, timeoutMS, status, respHeaders, sslFactory);
	}
	
	@Override  
    protected String getFallback() {  
        return "";  
    }  
	
	// #14(跨平台):请求目标是否本地回环(loopback)。回环一律直连、不走系统代理(见 doCmd setProxy)。
	private static boolean isLoopbackTarget(HttpUriRequest request){
		try{
			if(request == null || request.getURI() == null){ return false; }
			String host = request.getURI().getHost();
			if(host == null){ return false; }
			host = host.trim().toLowerCase();
			return host.equals("localhost")
				|| host.equals("127.0.0.1") || host.startsWith("127.")
				|| host.equals("::1") || host.equals("[::1]") || host.equals("0:0:0:0:0:0:0:1");
		}catch(Exception e){
			return false;
		}
	}

	public static String doCmd(String user, String password, HttpUriRequest request,
			Map<String, String> headers, String contenttype, int timeoutMS, HttpStatusCode status, SSLConnectionSocketFactory sslFactory) {
		return doCmd(user, password, request, headers, contenttype, timeoutMS, status, null, sslFactory);
	}
	
	public static String doCmd(String user, String password, HttpUriRequest request,
			Map<String, String> headers, String contenttype, int timeoutMS, HttpStatusCode status, Map<String, String> respHeadMap, 
			SSLConnectionSocketFactory sslFactory){
		try{
			// #14(跨平台):本地回环目标(127.0.0.1/localhost/::1,如内置排盘服务 :8899)一律直连、不走系统代理。
			// 开系统代理(Clash/v2ray 等)时 JVM -Djava.net.useSystemProxies=true 会把回环调用也塞进代理 →
			// 代理转发 127.0.0.1 卡顿/超时(12–17s)→「排盘失败:本地排盘服务未就绪」;重启/修复无效(代理配置持久)。
			// 外部请求(api.openai.com 等)仍照常走代理(getHttpHost),AI 流式 #9 不受影响。
			RequestConfig requestConfig = RequestConfig.custom().setConnectTimeout(timeoutMS).setSocketTimeout(timeoutMS).setProxy(isLoopbackTarget(request) ? null : HttpClientUtility.getHttpHost()).build();
			HttpClientBuilder builder = null;
			if(BraveHelper.existZipkin()){
				builder = BraveHelper.getHttpClientBuilder(request.getURI().toString());
			}else{
				builder = HttpClientBuilder.create();
			}
			builder.setDefaultRequestConfig(requestConfig);
			if(sslFactory == null) {
				builder.setSSLContext(HttpClientUtility.sslCtx).setSSLHostnameVerifier(HttpClientUtility.hostnameVerifier);				
			}else {
				builder.setSSLSocketFactory(sslFactory);
			}
			CloseableHttpClient client = builder.build();
			HttpClientContext localContext = null;
			if(!StringUtility.isNullOrEmpty(password)){
				CredentialsProvider credentialsProvider = new BasicCredentialsProvider();
				credentialsProvider.setCredentials(AuthScope.ANY, new UsernamePasswordCredentials(user, password));
				localContext = HttpClientContext.create();
				localContext.setCredentialsProvider(credentialsProvider);
			}

			try{
				if(!StringUtility.isNullOrEmpty(contenttype)){
					request.setHeader(HttpHeaders.CONTENT_TYPE, contenttype);
				}else{
					request.setHeader(HttpHeaders.CONTENT_TYPE, "application/json; charset=UTF-8");
				}
				Map<String, String> tmphead = headers;
				if(tmphead == null){
					tmphead = new HashMap<String, String>();
				}
				for(Entry<String, String> entry : tmphead.entrySet()){
					request.setHeader(entry.getKey(), entry.getValue());
				}
				try{
					String[] ips = IPUtility.getLocalIps();
					request.setHeader("LocalIp", ips[0]);
				}catch(Exception e){
				}
				
				Map<String, String> headermap = HttpClientUtility.getHeadersMap(request.getAllHeaders());
				
				CloseableHttpResponse response = client.execute(request, localContext);
				Map<String, String> repsheaders = HttpClientUtility.getHeadersMap(response.getAllHeaders());
				if(respHeadMap != null) {
					respHeadMap.putAll(repsheaders);
				}
				int statcode = response.getStatusLine().getStatusCode(); 
				if(statcode != 200){
					String reason = response.getStatusLine().getReasonPhrase();
					if(status != null){
						status.statCode = statcode;
						status.phase = reason;
					}
					String jsonheads = JsonUtility.encode(repsheaders);
					String requestjsonhead = JsonUtility.encode(redactSensitiveHeaders(headermap));
					String str = "";
					try{
						str = EntityUtils.toString(response.getEntity(), "UTF-8");
					}catch(Exception e){
					}
					String errmsg = String.format("Failed : HTTP error code : %d; reason : %s, request-header:%s, response-headers:%s, response-body:%s", 
							statcode, reason, requestjsonhead, jsonheads, str);
					throw new ErrorCodeException(statcode, errmsg);
				}

				String charset = "utf-8";
				if(!StringUtility.isNullOrEmpty(contenttype)){
					String[] parts = StringUtility.splitString(contenttype, ';');
					for(String part : parts){
						if(part.contains("=")){
							String[] cparts = StringUtility.splitString(part, '=');
							if(cparts[0].trim().equalsIgnoreCase("charset") && cparts.length > 1){
								charset = cparts[1].trim();
								break;
							}
						}
					}
				}
				String str = EntityUtils.toString(response.getEntity(), charset);
				return str;
			}catch(Exception e){
				HttpClientUtility.log.error("请求{}失败, cause:{}", stripQuery(request.getURI().toString()), e.getMessage());
				throw e;
			}finally{
				try{
					client.close();
				}catch(Exception e){
					e.printStackTrace();
				}
			}
		}catch(Exception e){
			throw new RuntimeException(e);
		}
	}

	// 出站请求失败时不要把凭据回显到错误信息/日志：屏蔽敏感请求头的值，保留其余头与响应体。
	static Map<String, String> redactSensitiveHeaders(Map<String, String> headers){
		Map<String, String> copy = new HashMap<String, String>();
		if(headers == null){
			return copy;
		}
		for(Entry<String, String> entry : headers.entrySet()){
			String key = entry.getKey() == null ? "" : entry.getKey().toLowerCase();
			boolean sensitive = key.equals("authorization") || key.equals("x-api-key")
				|| key.equals("api-key") || key.equals("apikey") || key.equals("x-goog-api-key")
				|| key.equals("cookie") || key.equals("set-cookie") || key.equals("proxy-authorization")
				|| key.equals("localip");
			copy.put(entry.getKey(), sensitive ? "***redacted***" : entry.getValue());
		}
		return copy;
	}

	// 去掉 URL 查询串，避免把 Gemini 等放在 ?key= 里的密钥写进日志。
	static String stripQuery(String uri){
		if(uri == null){
			return "";
		}
		int idx = uri.indexOf('?');
		return idx >= 0 ? uri.substring(0, idx) : uri;
	}
}

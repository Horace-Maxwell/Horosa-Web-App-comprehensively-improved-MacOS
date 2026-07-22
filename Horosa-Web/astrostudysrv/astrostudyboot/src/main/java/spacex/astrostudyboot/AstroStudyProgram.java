package spacex.astrostudyboot;

import org.apache.tomcat.util.http.LegacyCookieProcessor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.data.mongo.MongoDataAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.mongo.MongoAutoConfiguration;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.embedded.tomcat.TomcatServletWebServerFactory;
import org.springframework.boot.web.server.WebServerFactoryCustomizer;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ImportResource;

import com.thetransactioncompany.cors.CORSFilter;

import boundless.spring.help.interceptor.RSAFilter;
import boundless.utility.ProgArgsHelper;
import spacex.astrostudy.constants.ClientApp;
import spacex.basecomm.constants.ClientChannel;
import spacex.basecomm.helper.HttpHelper;
import spacex.basecomm.model.AppInfo;

@SpringBootApplication(exclude={MongoAutoConfiguration.class,MongoDataAutoConfiguration.class})
@EnableAutoConfiguration(exclude={DataSourceAutoConfiguration.class,MongoAutoConfiguration.class,MongoDataAutoConfiguration.class})
@ImportResource("classpath:conf/spring-config.xml")
public class AstroStudyProgram {

	public static void main(String[] args) {
		ProgArgsHelper.init(args);
		
		AppInfo info = new AppInfo();
		info.version = AstroStudyProgram.class.getPackage().getImplementationVersion();
		info.version = info.version == null ? "1.0.0" : info.version;
		info.app = ClientApp.AstroStudy.getCode() + "";
		info.channel = ClientChannel.Server.getCode() + "";
		HttpHelper.setAppInfo(info);
		
		SpringApplicationBuilder builder = new SpringApplicationBuilder(AstroStudyProgram.class).web(WebApplicationType.SERVLET);
		// 启动黑盒切分(测量轮专用,默认关零开销):HOROSA_JAVA_STARTUP_PROFILE=1 时缓冲
		// 全部 StartupStep,ready 后由 StartupLedgerListener 把最肥步骤写入启动账本。
		if ("1".equals(System.getenv("HOROSA_JAVA_STARTUP_PROFILE"))) {
			startupProfiler = new org.springframework.boot.context.metrics.buffering.BufferingApplicationStartup(8192);
			builder.application().setApplicationStartup(startupProfiler);
		}
		builder.run(args);
	}

	// 测量轮启动分析器句柄(默认 null;StartupLedgerListener 读取后落账)。
	static volatile org.springframework.boot.context.metrics.buffering.BufferingApplicationStartup startupProfiler = null;
	
	private CORSFilter newCORSFilter(){
		CORSFilter corsFilter = new CORSFilter();
		
		return corsFilter;
	}
	
	@Bean
	public FilterRegistrationBean<CORSFilter> corsingFilter(){
		CORSFilter corsFilter = newCORSFilter();
		FilterRegistrationBean<CORSFilter> registration = new FilterRegistrationBean<CORSFilter>();
		
		registration.setFilter(corsFilter);
		registration.addUrlPatterns("/*");
	    registration.addInitParameter("cors.allowOrigin", "*");
	    registration.addInitParameter("cors.supportedMethods", "GET, POST, HEAD, PUT, DELETE, OPTIONS, CONNECT, TRACE, PATCH");
	    registration.addInitParameter("cors.supportedHeaders", "Accept, Accept-Encoding, Accept-Language, Host, Origin, X-Requested-With, Content-Type, User-Agent, Content-Length, Last-Modified, Access-Control-Request-Headers, HTTP_X_REAL_IP, HTTP_X_FORWARDED_FOR, x-forwarded-for, Token, x-remote-IP, x-originating-IP, x-remote-addr, x-remote-ip, x-client-ip, x-client-IP, X-Real-ip, ImgTokenListName, SmsTokenListName, _IMGTOKENLIST, _SMSTOKENLIST, Signature, LocalIp, ClientChannel, ClientApp, ClientVer");
	    registration.addInitParameter("cors.exposedHeaders", "Set-Cookie, ResultCode, ResultMessage, ImgTokenListName, SmsTokenListName, Signature, NeedLogin, Encrypted, SimpleData, RawData");
	    registration.addInitParameter("cors.supportsCredentials", "true");
	    registration.setName("CORS");
	    registration.setOrder(1);
	    
	    return registration;
	}
	
	@Bean
    public WebServerFactoryCustomizer<TomcatServletWebServerFactory> cookieProcessorCustomizer() {
        return (factory)->factory.addContextCustomizers((context)->context.setCookieProcessor(new LegacyCookieProcessor()));
    }

	// 🔥 Hystrix 核心预热:进程内**首次执行任意 HystrixCommand** 会初始化 Hystrix 核心(RxJava 调度器 /
	// 指标发布 / 插件注册 / 线程池),约 1-2s(Hystrix 首用通病)。每次重启软件后,首个经 Java 转发 Python 的
	// 请求(无论哪个技法,如印度占星)都要吃这一下 → 表现为「重启后首次进入某技法卡 ~3s」。这里启动后用后台
	// 线程跑一个 trivial 命令把核心提前热好,后续真实转发不再付这笔冷启动。后台线程不阻塞启动;失败静默不影响服务。
	@Bean
	public CommandLineRunner hystrixCoreWarmup() {
		return (args) -> {
			Thread t = new Thread(() -> {
				try {
					new com.netflix.hystrix.HystrixCommand<String>(
							com.netflix.hystrix.HystrixCommandGroupKey.Factory.asKey("warmup")) {
						@Override
						protected String run() {
							return "ok";
						}
					}.execute();
				} catch (Throwable ignore) {
				}
			}, "hystrix-core-warmup");
			t.setDaemon(true);
			t.start();
		};
	}

//	@Bean
//	public FilterRegistrationBean<RSAFilter> rsaFilter(){
//		RSAFilter filter = new RSAFilter();
//		FilterRegistrationBean<RSAFilter> reg = new FilterRegistrationBean<RSAFilter>();
//		reg.setFilter(filter);
//		reg.setOrder(2);
//		
//		reg.addUrlPatterns("/*");
//		reg.setName("RSAFilter");
//		
//		return reg;
//	}
	

}

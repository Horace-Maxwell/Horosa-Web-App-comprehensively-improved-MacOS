package boundless.spring.help.interceptor;

import static org.junit.Assert.assertFalse;

import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.lang.reflect.Proxy;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;

import org.junit.After;
import org.junit.Test;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpOutputMessage;

public class JsonConverterTest {

	@After
	public void cleanup(){
		TransData.clearTransData();
	}

	@Test
	public void sseResponsesAreNeverEncrypted() throws Exception{
		JsonConverter converter = new JsonConverter();
		HttpOutputMessage output = new SimpleHttpOutputMessage();
		HashMap<String, Object> header = new HashMap<String, Object>();
		header.put("ClientApp", "1");
		TransData.setRequestData(header, new HashMap<String, Object>());
		TransData.setRequestObject(mockRequest(), null);
		TransData.setSSE(true);

		Method method = JsonConverter.class.getDeclaredMethod("needEncryp", org.springframework.http.HttpOutputMessage.class);
		method.setAccessible(true);
		boolean result = (Boolean) method.invoke(converter, output);

		assertFalse(result);
	}

	private static HttpServletRequest mockRequest(){
		Map<String, Object> attrs = new HashMap<String, Object>();
		return (HttpServletRequest) Proxy.newProxyInstance(
			JsonConverterTest.class.getClassLoader(),
			new Class[] { HttpServletRequest.class },
			(proxy, method, args)->{
				String name = method.getName();
				if("setAttribute".equals(name)) {
					attrs.put(String.valueOf(args[0]), args[1]);
					return null;
				}
				if("getAttribute".equals(name)) {
					return attrs.get(String.valueOf(args[0]));
				}
				Class<?> returnType = method.getReturnType();
				if(returnType.equals(boolean.class)) {
					return false;
				}
				if(returnType.equals(int.class) || returnType.equals(short.class) || returnType.equals(byte.class)) {
					return 0;
				}
				if(returnType.equals(long.class)) {
					return 0L;
				}
				if(returnType.equals(float.class)) {
					return 0f;
				}
				if(returnType.equals(double.class)) {
					return 0d;
				}
				return null;
			}
		);
	}

	private static class SimpleHttpOutputMessage implements HttpOutputMessage {
		private final HttpHeaders headers = new HttpHeaders();
		private final ByteArrayOutputStream body = new ByteArrayOutputStream();

		@Override
		public OutputStream getBody(){
			return body;
		}

		@Override
		public HttpHeaders getHeaders(){
			return headers;
		}
	}
}

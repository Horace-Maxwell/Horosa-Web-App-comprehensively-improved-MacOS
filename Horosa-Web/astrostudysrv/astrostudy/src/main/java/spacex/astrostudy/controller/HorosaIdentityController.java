package spacex.astrostudy.controller;

import javax.servlet.http.HttpServletResponse;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

/**
 * 本地后端身份握手端点。
 *
 * 前端在采用任何本地服务地址(query / 存储 / 端口推导)之前,先 GET 本端点核验:
 * app 标记必须为 horosa-backend,且(页面无期望 nonce 或 nonce 一致)才视为真后端;
 * 否则一律拒绝——防止端口被其它进程占用时把「陌生 200 响应」误当后端(会表现为
 * 排盘失败但 statusCode:200)。
 *
 * 设计约束:
 * - 明文 JSON、无鉴权、不走 TransData 信封:身份核验发生在协议/加密协商之前;
 * - 直写 HttpServletResponse 并 flush,绕开统一响应改写,保证任何环境下格式稳定;
 * - 仅回环可达(server.address=127.0.0.1),不含任何敏感信息;
 * - nonce 来自壳注入的 HOROSA_LAUNCH_NONCE(每次启动会话一枚),浏览器直连开发场景无
 *   nonce 时字段为空串,前端只校验 app 标记。
 */
@Controller
public class HorosaIdentityController {

	@RequestMapping(value = "/horosaIdentity", method = RequestMethod.GET)
	public void execute(HttpServletResponse response) throws Exception {
		String nonce = System.getenv("HOROSA_LAUNCH_NONCE");
		if (nonce == null) {
			nonce = "";
		}
		// 手写 JSON:nonce 白名单过滤为 [A-Za-z0-9_-],无注入面。
		String body = "{\"app\":\"horosa-backend\",\"proto\":1,\"nonce\":\""
				+ nonce.replaceAll("[^A-Za-z0-9_-]", "") + "\"}";
		response.setStatus(200);
		response.setContentType("application/json;charset=UTF-8");
		response.setHeader("Cache-Control", "no-store");
		response.getWriter().write(body);
		response.getWriter().flush();
	}

}

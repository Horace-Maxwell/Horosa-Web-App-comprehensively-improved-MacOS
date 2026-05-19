package spacex.astrostudycn.controller;

import java.util.Collections;
import java.util.Map;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import boundless.exception.ErrorCodeException;
import boundless.spring.help.interceptor.TransData;
import spacex.astrostudycn.service.QizhengMoiraRuleService;

@Controller
@RequestMapping("/qizheng")
public class QizhengMoiraController {

	private final QizhengMoiraRuleService moiraRuleService = new QizhengMoiraRuleService();

	@ResponseBody
	@RequestMapping("/moira")
	public void moira() {
		Object chartObj = TransData.get("chartObj");
		if(!(chartObj instanceof Map)) {
			throw new ErrorCodeException(100101, "miss.qizheng.chartObj");
		}
		Map<String, Object> params = Collections.emptyMap();
		Object paramsObj = TransData.get("params");
		if(paramsObj instanceof Map) {
			params = (Map<String, Object>) paramsObj;
		}
		Map<String, Object> res = moiraRuleService.analyze((Map<String, Object>) chartObj, params);
		TransData.set(res);
	}
}

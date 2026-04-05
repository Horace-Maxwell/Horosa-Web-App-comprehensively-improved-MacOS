package spacex.astrostudy.controller;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import boundless.spring.help.interceptor.SseHelper;
import boundless.spring.help.interceptor.TransData;
import boundless.utility.JsonUtility;
import spacex.astrostudy.service.AIAnalysisMaterialService;
import spacex.astrostudy.service.AIAnalysisProxyService;

@Controller
@RequestMapping("/aianalysis")
public class AIAnalysisController {

	@Autowired
	private AIAnalysisProxyService service;

	@Autowired
	private AIAnalysisMaterialService materialService;

	@RequestMapping("/providers/models")
	@ResponseBody
	public void listModels(){
		Map<String, Object> result = service.listModels(readParams());
		TransData.set("Result", result);
	}

	@RequestMapping("/chat")
	@ResponseBody
	public void chat(){
		Map<String, Object> result = service.chat(readParams());
		TransData.set("Result", result);
	}

	@RequestMapping("/chat/stream")
	@ResponseBody
	public SseEmitter chatStream(){
		final Map<String, Object> params = readParams();
		final SseEmitter emitter = SseHelper.push(UUID.randomUUID().toString());
		final HttpServletRequest request = TransData.getRequestObject();
		final HttpServletResponse response = TransData.getResponseObject();
		Thread worker = new Thread(()->{
			TransData.setRequestData(new LinkedHashMap<String, Object>(), new LinkedHashMap<String, Object>());
			TransData.setRequestObject(request, response);
			SseHelper.markCurrentThread();
			try {
				// Give the servlet async pipeline a moment to fully enter SSE mode
				// before the first frame; some desktop runtime starts otherwise prepend
				// the default encrypted response body ahead of the event stream.
				Thread.sleep(50L);
			}catch(InterruptedException e) {
				Thread.currentThread().interrupt();
			}
			service.chatStream(params, emitter);
		}, "ai-analysis-chat-stream");
		worker.setDaemon(true);
		worker.start();
		return emitter;
	}

	@RequestMapping("/providers/diagnose")
	@ResponseBody
	public void diagnoseProvider(){
		Map<String, Object> result = service.diagnose(readParams());
		TransData.set("Result", result);
	}

	@RequestMapping("/materials/extract")
	@ResponseBody
	public void extractMaterial(){
		Map<String, Object> result = materialService.extract(readParams());
		TransData.set("Result", result);
	}

	@RequestMapping("/embeddings")
	@ResponseBody
	public void embeddings(){
		Map<String, Object> result = service.embeddings(readParams());
		TransData.set("Result", result);
	}

	private Map<String, Object> readParams(){
		String json = TransData.getRequestJson();
		Map<String, Object> result = JsonUtility.toDictionary(json);
		return result == null ? new LinkedHashMap<String, Object>() : result;
	}
}

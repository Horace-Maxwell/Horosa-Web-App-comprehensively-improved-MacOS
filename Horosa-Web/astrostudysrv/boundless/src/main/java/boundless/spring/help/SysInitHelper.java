package boundless.spring.help;

import java.lang.reflect.Method;
import java.util.List;
import java.util.Map;

import boundless.log.AppLoggers;
import boundless.log.QueueLog;
import boundless.utility.ConvertUtility;
import boundless.utility.StringUtility;

public class SysInitHelper {

	public static final String TaskBeanKey = "taskBean";
	public static final String TaskClassKey = "taskClass";
	public static final String InitMethodKey = "initMethod";
	public static final String InitMethodParamKey = "initMethodParam";
	
	private static boolean flagEnabled(String key) {
		if(StringUtility.isNullOrEmpty(key)) {
			return true;
		}
		String value = System.getProperty(key);
		if(StringUtility.isNullOrEmpty(value)) {
			value = System.getenv(key);
		}
		if(StringUtility.isNullOrEmpty(value)) {
			return true;
		}
		value = value.trim();
		return !("0".equals(value) || "false".equalsIgnoreCase(value) || "off".equalsIgnoreCase(value));
	}

	public void setParameters(Map<String, Object> param){
		
		String className = ConvertUtility.getValueAsString(param.get(TaskClassKey));
		String initMethod = ConvertUtility.getValueAsString(param.get(InitMethodKey));
		String initMethodParam = ConvertUtility.getValueAsString(param.get(InitMethodParamKey));
		if("spacex.astrostudy.helper.TransGroupHelper".equals(className) && !flagEnabled("HOROSA_ENABLE_STARTUP_TRANSGROUP_INIT")) {
			return;
		}
		Object bean = param.get(TaskBeanKey);
		try{
			Class clazz = null;
			if(bean != null){
				clazz = bean.getClass();
			}else{
				clazz = Class.forName(className);
			}
			Method initM = null;
			if(!StringUtility.isNullOrEmpty(initMethod)){
				if(initMethod.equalsIgnoreCase("init") || initMethod.equalsIgnoreCase("clinit")){
					throw new RuntimeException("cannot use 'init' or 'clinit' as method name");
				}
				if(StringUtility.isNullOrEmpty(initMethodParam)){
					initM = clazz.getMethod(initMethod);
				}else{
					initM = clazz.getMethod(initMethod, String.class);
				}
			}
			if(initM != null){
				if(StringUtility.isNullOrEmpty(initMethodParam)){
					initM.invoke(bean);
				}else{
					initM.invoke(bean, initMethodParam);
				}
			}
			
		}catch(Exception e){
			Throwable err = e.getCause();
			if(err == null){
				err = e;
			}
			QueueLog.error(AppLoggers.ErrorLogger, err);
			throw new RuntimeException(e);
		}
	}
	
	public void setTasks(List<Map<String, Object>> tasks){
		for(Map<String, Object> params : tasks){
			try{
				setParameters(params);
			}catch(Exception e){
				QueueLog.error(AppLoggers.ErrorLogger, e);
			}
		}
	}
	
	
}

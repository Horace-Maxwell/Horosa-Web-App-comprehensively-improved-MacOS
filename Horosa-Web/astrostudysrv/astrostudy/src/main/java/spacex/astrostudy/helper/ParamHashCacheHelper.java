package spacex.astrostudy.helper;

import java.lang.reflect.Array;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;
import java.util.stream.Stream;

import boundless.log.AppLoggers;
import boundless.log.QueueLog;
import boundless.security.MD5Utility;
import boundless.spring.help.PropertyPlaceholder;
import boundless.types.ICache;
import boundless.utility.ConvertUtility;
import boundless.utility.FormatUtility;
import boundless.utility.JsonUtility;
import boundless.utility.StringUtility;

public class ParamHashCacheHelper {

	private static final String Prefix = PropertyPlaceholder.getProperty("paramhash.cache.prefix", "paramhash");
	private static final boolean EnableCache = PropertyPlaceholder.getPropertyAsBool("paramhash.cache.enable", true);
	private static final boolean EnableRedis = PropertyPlaceholder.getPropertyAsBool("paramhash.cache.redis.enable", true);
	private static final boolean EnableLocal = PropertyPlaceholder.getPropertyAsBool("paramhash.cache.local.enable", true);
	private static final int ExpireInSec = PropertyPlaceholder.getPropertyAsInt("paramhash.cache.expireinsecond", 86400);
	private static final int AnnualExpireInSec = PropertyPlaceholder.getPropertyAsInt("paramhash.cache.annual.expireinsecond", 86400 * 180);
	private static final String LocalDir = PropertyPlaceholder.getProperty("paramhash.cache.local.dir", defaultLocalDir());
	private static final DateTimeFormatter LdtFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

	private static final ICache RedisCache = CacheHelper.getCache();
	private static final ConcurrentHashMap<String, Object> KeyLocks = new ConcurrentHashMap<String, Object>();

	private static final class LocalPayload {
		Object value;
		boolean expired;
	}

	private ParamHashCacheHelper() {
	}

	private static String defaultLocalDir() {
		String workingDir = System.getProperty("user.dir", ".");
		return Paths.get(workingDir, ".horosa-cache", "paramhash").toString();
	}

	public static Object get(String scope, Map<String, Object> params, Function<Map<String, Object>, Object> fun) {
		return get(scope, params, fun, ExpireInSec);
	}

	public static Object getAnnual(String scope, Map<String, Object> params, Function<Map<String, Object>, Object> fun) {
		return get(scope, params, fun, AnnualExpireInSec);
	}

	public static Object get(String scope, Map<String, Object> params, Function<Map<String, Object>, Object> fun, int expInSec) {
		Map<String, Object> req = new HashMap<String, Object>();
		if(params != null) {
			req.putAll(params);
		}
		if(fun == null) {
			return null;
		}
		if(!EnableCache) {
			return fun.apply(new HashMap<String, Object>(req));
		}

		String cacheKey = buildCacheKey(scope, req);
		Object obj = getFromRedis(cacheKey);
		if(obj != null) {
			return obj;
		}

		String cleanScope = sanitizeScope(scope);
		String hash = hash(req);
		LocalPayload local = getFromLocal(cleanScope, hash, expInSec);
		if(local.expired) {
			removeRedis(cacheKey);
		}
		if(local.value != null) {
			saveToRedis(cacheKey, local.value, expInSec);
			return local.value;
		}

		Object keylock = KeyLocks.computeIfAbsent(cacheKey, (k)-> new Object());
		try {
			synchronized (keylock) {
				obj = getFromRedis(cacheKey);
				if(obj != null) {
					return obj;
				}

				local = getFromLocal(cleanScope, hash, expInSec);
				if(local.expired) {
					removeRedis(cacheKey);
				}
				if(local.value != null) {
					saveToRedis(cacheKey, local.value, expInSec);
					return local.value;
				}

				obj = fun.apply(new HashMap<String, Object>(req));
				if(isCacheable(obj)) {
					saveToRedis(cacheKey, obj, expInSec);
					saveToLocal(cleanScope, hash, obj, expInSec);
				}
				return obj;
			}
		} finally {
			Object current = KeyLocks.get(cacheKey);
			if(current == keylock) {
				KeyLocks.remove(cacheKey);
			}
		}
	}

	public static long clearByScope(String scopePrefix) {
		String scope = sanitizeScope(scopePrefix);
		long removed = 0;
		try {
			String prefix = CacheHelper.buildCacheKey(Prefix, scope);
			removed += CacheHelper.getCache().removeMany(prefix + "*");
		} catch(Exception e) {
			QueueLog.error(AppLoggers.ErrorLogger, e);
		}

		if(!EnableLocal) {
			return removed;
		}
		try {
			Path localRoot = Paths.get(LocalDir);
			if(!Files.exists(localRoot)) {
				return removed;
			}
			List<Path> targets = new ArrayList<Path>();
			try(Stream<Path> list = Files.list(localRoot)) {
				list.forEach((p)->{
					if(!Files.isDirectory(p)) {
						return;
					}
					String name = p.getFileName().toString();
					if(name.startsWith(scope)) {
						targets.add(p);
					}
				});
			}
			for(Path target : targets) {
				List<Path> paths = new ArrayList<Path>();
				try(Stream<Path> walk = Files.walk(target)) {
					walk.forEach((p)->{
						paths.add(p);
					});
				}
				paths.sort((a, b)-> b.getNameCount() - a.getNameCount());
				for(Path p : paths) {
					try {
						if(Files.isDirectory(p)) {
							Files.deleteIfExists(p);
						}else {
							if(Files.deleteIfExists(p)) {
								removed++;
							}
						}
					}catch(Exception e) {
						QueueLog.error(AppLoggers.ErrorLogger, e);
					}
				}
			}
		}catch(Exception e) {
			QueueLog.error(AppLoggers.ErrorLogger, e);
		}
		return removed;
	}

	public static String buildCacheKey(String scope, Map<String, Object> params) {
		String hash = hash(params);
		String cleanScope = sanitizeScope(scope);
		return CacheHelper.buildCacheKey(Prefix, cleanScope, hash);
	}

	public static String hash(Map<String, Object> params) {
		Object normalized = normalize(params);
		String json = JsonUtility.encode(normalized);
		return MD5Utility.encryptAsString(json);
	}

	private static String sanitizeScope(String scope) {
		String value = StringUtility.isNullOrEmpty(scope) ? "default" : scope;
		return value.replaceAll("[^A-Za-z0-9._-]", "_");
	}

	private static Object normalize(Object obj) {
		if(obj == null) {
			return null;
		}
		if(obj instanceof Enum<?>) {
			return ((Enum<?>) obj).name();
		}
		if(obj instanceof Date) {
			return FormatUtility.formatDateTime((Date)obj, "yyyy-MM-dd HH:mm:ss");
		}
		if(obj instanceof LocalDateTime) {
			return ((LocalDateTime)obj).format(LdtFormatter);
		}
		if(obj instanceof ZonedDateTime) {
			return ((ZonedDateTime)obj).toOffsetDateTime().format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
		}
		if(obj instanceof Map<?, ?>) {
			Map<?, ?> map = (Map<?, ?>) obj;
			TreeMap<String, Object> sorted = new TreeMap<String, Object>();
			for(Map.Entry<?, ?> entry : map.entrySet()) {
				String key = entry.getKey() == null ? "null" : entry.getKey().toString();
				sorted.put(key, normalize(entry.getValue()));
			}
			return sorted;
		}
		if(obj instanceof Collection<?>) {
			Collection<?> col = (Collection<?>) obj;
			List<Object> list = new ArrayList<Object>(col.size());
			for(Object item : col) {
				list.add(normalize(item));
			}
			return list;
		}
		Class<?> clz = obj.getClass();
		if(clz.isArray()) {
			int len = Array.getLength(obj);
			List<Object> list = new ArrayList<Object>(len);
			for(int i = 0; i < len; i++) {
				list.add(normalize(Array.get(obj, i)));
			}
			return list;
		}
		return obj;
	}

	private static Object getFromRedis(String key) {
		if(!EnableRedis || RedisCache == null || StringUtility.isNullOrEmpty(key)) {
			return null;
		}
		try {
			Object obj = RedisCache.get(key);
			if(obj == null) {
				return null;
			}
			if(obj instanceof String) {
				String str = (String)obj;
				if(StringUtility.isNullOrEmpty(str)) {
					return null;
				}
				try {
					return JsonUtility.decode(str, Object.class);
				}catch(Exception e) {
					return str;
				}
			}
			return obj;
		}catch(Exception e) {
			QueueLog.error(AppLoggers.ErrorLogger, e);
			return null;
		}
	}

	private static void saveToRedis(String key, Object value, int expInSec) {
		if(!EnableRedis || RedisCache == null || value == null || StringUtility.isNullOrEmpty(key)) {
			return;
		}
		try {
			if(expInSec > 0) {
				RedisCache.put(key, value, expInSec);
			}else {
				RedisCache.put(key, value);
			}
		}catch(Exception e) {
			QueueLog.error(AppLoggers.ErrorLogger, e);
		}
	}

	private static void removeRedis(String key) {
		if(!EnableRedis || RedisCache == null || StringUtility.isNullOrEmpty(key)) {
			return;
		}
		try {
			RedisCache.remove(key);
		}catch(Exception e) {
			QueueLog.error(AppLoggers.ErrorLogger, e);
		}
	}

	private static LocalPayload getFromLocal(String scope, String hash, int expInSec) {
		LocalPayload payload = new LocalPayload();
		payload.value = null;
		payload.expired = false;
		if(!EnableLocal) {
			return payload;
		}
		Path path = localPath(scope, hash);
		if(path == null || !Files.exists(path)) {
			return payload;
		}
		try {
			String text = Files.readString(path, StandardCharsets.UTF_8);
			if(StringUtility.isNullOrEmpty(text)) {
				return payload;
			}
			Object obj = JsonUtility.decode(text, Object.class);
			if(!(obj instanceof Map)) {
				return payload;
			}
			Map<String, Object> map = (Map<String, Object>) obj;
			long now = System.currentTimeMillis();
			long expAt = ConvertUtility.getValueAsLong(map.get("expAt"), 0);
			if(expAt <= 0 && expInSec > 0) {
				expAt = ConvertUtility.getValueAsLong(map.get("createdAt"), 0) + expInSec * 1000L;
			}
			if(expAt > 0 && expAt <= now) {
				payload.expired = true;
				try {
					Files.deleteIfExists(path);
				}catch(Exception e) {
					QueueLog.error(AppLoggers.ErrorLogger, e);
				}
				return payload;
			}
			payload.value = map.get("value");
			return payload;
		}catch(Exception e) {
			QueueLog.error(AppLoggers.ErrorLogger, e);
			return payload;
		}
	}

	private static void saveToLocal(String scope, String hash, Object value, int expInSec) {
		if(!EnableLocal || value == null) {
			return;
		}
		if(!canPersistLocal(value)) {
			return;
		}
		Path path = localPath(scope, hash);
		if(path == null) {
			return;
		}
		try {
			Files.createDirectories(path.getParent());
			long now = System.currentTimeMillis();
			Map<String, Object> wrap = new HashMap<String, Object>();
			wrap.put("createdAt", now);
			wrap.put("expAt", expInSec > 0 ? now + expInSec * 1000L : 0L);
			wrap.put("value", value);
			String json = JsonUtility.encode(wrap);
			Path tmp = Paths.get(path.toString() + ".tmp");
			Files.writeString(tmp, json, StandardCharsets.UTF_8);
			try {
				Files.move(tmp, path, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
			}catch(AtomicMoveNotSupportedException e) {
				Files.move(tmp, path, StandardCopyOption.REPLACE_EXISTING);
			}
		}catch(Exception e) {
			QueueLog.error(AppLoggers.ErrorLogger, e);
		}
	}

	private static Path localPath(String scope, String hash) {
		if(StringUtility.isNullOrEmpty(LocalDir) || StringUtility.isNullOrEmpty(hash)) {
			return null;
		}
		String prefix = hash.length() >= 2 ? hash.substring(0, 2) : "00";
		return Paths.get(LocalDir, scope, prefix, hash + ".json");
	}

	private static boolean isCacheable(Object obj) {
		if(obj == null) {
			return false;
		}
		if(obj instanceof Map) {
			return !((Map<?, ?>) obj).isEmpty();
		}
		if(obj instanceof Collection) {
			return !((Collection<?>) obj).isEmpty();
		}
		return true;
	}

	private static boolean canPersistLocal(Object obj) {
		if(obj == null) {
			return true;
		}
		if(obj instanceof String || obj instanceof Number || obj instanceof Boolean) {
			return true;
		}
		if(obj instanceof Map<?, ?>) {
			Map<?, ?> map = (Map<?, ?>) obj;
			for(Object val : map.values()) {
				if(!canPersistLocal(val)) {
					return false;
				}
			}
			return true;
		}
		if(obj instanceof Collection<?>) {
			Collection<?> col = (Collection<?>) obj;
			for(Object item : col) {
				if(!canPersistLocal(item)) {
					return false;
				}
			}
			return true;
		}
		if(obj.getClass().isArray()) {
			int len = Array.getLength(obj);
			for(int i = 0; i < len; i++) {
				if(!canPersistLocal(Array.get(obj, i))) {
					return false;
				}
			}
			return true;
		}
		return false;
	}
}

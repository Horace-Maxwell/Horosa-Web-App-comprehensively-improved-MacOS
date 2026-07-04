package spacex.astrostudyboot;

import java.lang.management.ManagementFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.stereotype.Component;

import spacex.astrostudycn.model.OnlyFourColumns;

/**
 * 结构化启动账本(Java 层写入端)+ 进程内自热身(WS-3b)。
 *
 * 账本:四层进程(Rust/shell/Java/Python)经 env 共享同一 JSON Lines 文件:
 *   HOROSA_LEDGER_FILE      账本文件绝对路径(缺省=不写,零开销)
 *   HOROSA_RUN_TAG          本次启动运行标签(四层同值,可按 run 聚合)
 *   HOROSA_STARTUP_LEDGER=0 总开关(默认开)
 * 段 java.jvm_to_ctx_ready:JVM 进程起点(RuntimeMXBean.getStartTime,含 JVM 自身
 * 初始化)到 Spring ApplicationReadyEvent 的毫秒——Java 侧启动黑盒的单一权威数字。
 *
 * 自热身:ready 后 daemon 线程异步把「就绪后第一下点击」要付的冷类加载/JIT/历法表
 * 初始化成本挪进空闲(进程内直调计算类,不走 HTTP/RSA,不占启动关键路径,不与
 * 用户请求抢连接)。段 java.self_warmup{ms};HOROSA_JAVA_SELF_WARMUP=0 关。
 * 写入 append + best-effort 吞错:账本与热身绝不影响业务。
 */
@Component
public class StartupLedgerListener implements ApplicationListener<ApplicationReadyEvent> {

    @Override
    public void onApplicationEvent(ApplicationReadyEvent event) {
        ledgerMark("java.jvm_to_ctx_ready", jvmUptimeMs());
        selfWarmupAsync();
    }

    private static long jvmUptimeMs() {
        return System.currentTimeMillis() - ManagementFactory.getRuntimeMXBean().getStartTime();
    }

    private static void selfWarmupAsync() {
        String flag = System.getenv("HOROSA_JAVA_SELF_WARMUP");
        if (flag != null && ("0".equals(flag) || "false".equalsIgnoreCase(flag))) {
            return;
        }
        Thread warm = new Thread(() -> {
            try {
                // 让端口就绪轮询/首屏导航先行,热身贴在其后的空闲里。
                Thread.sleep(1500);
                long t0 = System.currentTimeMillis();
                // 八字全链(历法/JDN/节气/干支表)×3 组日期:类加载 + 常用路径 JIT。
                String[][] samples = {
                        {"1984-02-04 10:30:00", "+08:00", "116e28", "39n54"},
                        {"2000-09-15 22:05:00", "+08:00", "121e28", "31n14"},
                        {"1976-07-06 21:11:00", "+08:00", "119e18", "26n05"},
                };
                for (String[] s : samples) {
                    OnlyFourColumns bz = new OnlyFourColumns(1, s[0], s[1], s[2], s[3], false, true);
                    bz.getNongli();
                }
                ledgerMark("java.self_warmup", System.currentTimeMillis() - t0);
            } catch (Throwable ignore) {
                // 热身 best-effort:失败静默,首点回到「冷即付」的现状语义。
            }
        }, "horosa-self-warmup");
        warm.setDaemon(true);
        warm.setPriority(Thread.MIN_PRIORITY);
        warm.start();
    }

    private static void ledgerMark(String seg, long ms) {
        try {
            String ledgerFile = System.getenv("HOROSA_LEDGER_FILE");
            String enabled = System.getenv("HOROSA_STARTUP_LEDGER");
            if (ledgerFile == null || ledgerFile.isEmpty()) {
                return;
            }
            if (enabled != null && ("0".equals(enabled) || "false".equalsIgnoreCase(enabled))) {
                return;
            }
            String runTag = System.getenv("HOROSA_RUN_TAG");
            long pid = ManagementFactory.getRuntimeMXBean().getPid();
            String row = String.format(
                    "{\"run\":\"%s\",\"layer\":\"java\",\"seg\":\"%s\",\"pid\":%d,\"ms\":%d}%n",
                    runTag == null ? "" : runTag.replace("\"", ""), seg, pid, ms);
            Path path = Paths.get(ledgerFile);
            Files.write(path, row.getBytes(StandardCharsets.UTF_8),
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (Throwable ignore) {
            // 账本 best-effort:任何异常吞掉,绝不影响服务启动。
        }
    }
}

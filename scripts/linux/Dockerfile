# 星阙批量验证的容器镜像(可选;不用容器就照 HEADLESS.md「批量验证」在主机上装 Node / Python / JDK)。
# 在解开的批量运行包(./horosa batch-pack 打出的 horosa-batch-<版本>/)目录里构建:docker build -f scripts/linux/Dockerfile -t horosa-batch .
# 运行(命例文件与输出放在挂载目录里):
#   docker run --rm -v "$PWD/work:/work" horosa-batch /work/cases.csv -t bazi,astrochart -o /work/out.jsonl -j 4
# 镜像里起一套计算服务(Python 排盘服务 + Java 后端)再跑批量;要多套:-e HOROSA_BACKEND_PAIRS=4(批量的并行数缺省随之 = 2 × 套数)。
FROM python:3.12-slim-bookworm

# Node 18(Debian bookworm 自带)与 JDK 17 的无图形界面运行时;build-essential 给没有预编译轮子的 Python 包现编用
RUN apt-get update \
 && apt-get install -y --no-install-recommends nodejs openjdk-17-jre-headless curl build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/horosa
COPY scripts/requirements/ scripts/requirements/
RUN python3 -m pip install --no-cache-dir -r scripts/requirements/linux-python.txt

# 运行包目录整个拷进镜像(无头运行时产物 + jsdom + Python 引擎源码与星历 + 后端 jar + 起停脚本)
COPY . .

ENV HOROSA_HOME=/var/lib/horosa \
    HOROSA_PYTHON=python3 \
    HOROSA_JAVA_BIN=java \
    HOROSA_SERVER_PORT=9999 \
    HOROSA_CHART_PORT=8899

# 入口:起计算服务 → 跑批量(参数原样交给 horosa-batch)→ 停服务
RUN printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail' \
  'pairs="${HOROSA_BACKEND_PAIRS:-1}"' \
  'bash scripts/linux/backends.sh start --pairs "${pairs}" >&2' \
  'spec=""; for i in $(seq 0 $((pairs - 1))); do spec="${spec}${spec:+,}$((HOROSA_SERVER_PORT + i)):$((HOROSA_CHART_PORT + i))"; done' \
  'set +e; ./horosa-batch "$@" --backends "${spec}"; rc=$?; set -e' \
  'bash scripts/linux/backends.sh stop --pairs "${pairs}" >&2 || true' \
  'exit "${rc}"' > /usr/local/bin/horosa-batch-entry && chmod +x /usr/local/bin/horosa-batch-entry

ENTRYPOINT ["/usr/local/bin/horosa-batch-entry"]

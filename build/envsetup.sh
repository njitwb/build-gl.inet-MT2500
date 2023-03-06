export TOP_DIR=/data/work/build-gl.inet-MT2500
export BUILD_DIR=${TOP_DIR}/out
export GL_UI=false
export CONFIG_FILE=${TOP_DIR}/devices/mt2500/setup_config.yml
export PROFILES_DIR=${TOP_DIR}/devices/mt2500/profiles
export PROFILES="target_mt7981_gl-mt2500 luci custom glinet_depends glinet_nas"
export GOPROXY=https://proxy.golang.com.cn,direct
export GL_PKGDIR=/data/work/build-gl.inet-MT2500/out/gl_sdk/mt7981

echo "include build/main.mk" > ${TOP_DIR}/Makefile

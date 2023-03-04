export TOP_DIR=/data/work/build-gl.inet-MT2500
export BUILD_DIR=${TOP_DIR}/out
export GL_UI=false
export CONFIG_FILE=${TOP_DIR}/devices/mt2500/setup_config.yml
export PROFILES_DIR=${TOP_DIR}/devices/mt2500/profiles
export PROFILES="target_mt7981_gl-mt2500 luci"

echo "include build/main.mk" > ${TOP_DIR}/Makefile

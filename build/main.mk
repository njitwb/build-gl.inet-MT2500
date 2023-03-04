# Makefile for MT2500 build

empty:=
space:= $(empty) $(empty)
$(if $(findstring $(space),$(TOP_DIR)),$(error ERROR: The path to the build directory must not include any spaces))

clean:
	@echo 清理编译...
	@test -d $(BUILD_DIR)/openwrt && $(MAKE) -C $(BUILD_DIR)/openwrt clean || echo "$(BUILD_DIR)/openwrt 目录不存在..."

distclean:
	@echo 彻底清除编译...
	@rm -rf $(BUILD_DIR)

setup:
	@echo setup workspace...
	@echo CONFIG_FILE=$(CONFIG_FILE)
	@echo PROFILES=$(PROFILES)
	@echo GL_UI=$(GL_UI)
	@$(TOP_DIR)/build/setup.py -c $(CONFIG_FILE)

all: setup
	$(MAKE) -C $(BUILD_DIR)/openwrt

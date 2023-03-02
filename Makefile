# Makefile for MT2500 build

TOPDIR:=$(CURDIR)
BUILD_DIR:=$(TOPDIR)/build_dir
export TOPDIR

empty:=
space:= $(empty) $(empty)
$(if $(findstring $(space),$(TOPDIR)),$(error ERROR: The path to the build directory must not include any spaces))

clean:
	@echo 清理编译...
	@test -d $(BUILD_DIR) && $(MAKE) -C $(BUILD_DIR) || echo "$(BUILD_DIR) 目录不存在..."

distclean:
	@echo 彻底清除编译...
	@rm -rf $(BUILDDIR)

all:


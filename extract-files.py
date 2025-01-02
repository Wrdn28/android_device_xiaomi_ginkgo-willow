#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#
from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    "hardware/qcom-caf/sm8150",
    "hardware/qcom-caf/wlan",
    "hardware/xiaomi",
    "vendor/qcom/opensource/commonsys/display",
    "vendor/qcom/opensource/commonsys-intf/display",
    "vendor/qcom/opensource/dataservices",
    "vendor/qcom/opensource/data-ipa-cfg-mgr-legacy-um",
    "vendor/qcom/opensource/display",
]
def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None
lib_fixups: lib_fixups_user_type = {
    libs_clang_rt_ubsan: lib_fixup_remove_arch_suffix,
    libs_proto_3_9_1: lib_fixup_vendorcompat,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libmmosal',
        'vendor.qti.hardware.fm@1.0',
        'vendor.qti.imsrtpservice@3.0',
    ): lib_fixup_vendor_suffix,
    (
        'libOmxCore',
        'libwfdaac_vendor',
        'libwpa_client',
    ): lib_fixup_remove,
}

# Blob fixups for specific files
blob_fixups: blob_fixups_user_type = {
    'vendor/etc/camera/camera_config.xml': blob_fixup()
        .custom_fixup(lambda path, dest: _remove_vtcamera(path, dest)),
    'vendor/lib64/libvendor.goodix.hardware.interfaces.biometrics.fingerprint@2.1.so': blob_fixup()
        .replace_needed('libhidlbase.so', 'libhidlbase-v32.so'),
    ('vendor/lib64/libwvhidl.so', 'vendor/lib64/mediadrm/libwvdrmengine.so', 'vendor/lib/mediadrm/libwvdrmengine.so'): blob_fixup()
        .replace_needed('libcrypto.so', 'libcrypto-v33.so'),
    ('vendor/lib/libstagefright_soft_ac4dec.so', 'vendor/lib/libstagefright_soft_ddpdec.so', 'vendor/lib/libstagefrightdolby.so', 'vendor/lib64/libdlbdsservice.so', 'vendor/lib64/libstagefright_soft_ac4dec.so', 'vendor/lib64/libstagefright_soft_ddpdec.so', 'vendor/lib64/libstagefrightdolby.so'): blob_fixup()
        .replace_needed('libstagefright_foundation-v33.so', 'libstagefright_foundation.so', 'libstagefright_foundation-v33.so'),

}

# Custom fixup function for 'camera_config.xml'
def _remove_vtcamera(path: str, dest: str):
    with open(dest, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        inside_module_config = False
        for line in lines:
            if "<CameraModuleConfig>" in line:
                inside_module_config = True
            if inside_module_config and "ginkgo_vtcamera" in line:
                inside_module_config = False
            if "</CameraModuleConfig>" in line:
                inside_module_config = False
            if not inside_module_config:
                file.write(line)
        file.truncate()

# Define the module for extraction
module = ExtractUtilsModule(
    'ginkgo',
    'xiaomi',
    blob_fixups=blob_fixups,
    namespace_imports=namespace_imports,
    check_elf=True,
)

# Main execution
if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()

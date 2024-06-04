#!/usr/bin/env python

import time
from zenlite_sdk import *
from zen_logger import ZLOG

_TOTAL_RUN_SECONDS = 12 * 3600  # seconds

# FIXME: update Device name
_TARGET_DEVICE_NAME = "OxyZen-Test"

# Model Number: ZS11
# Serial Number: BCZS11175B220000C
_target_device: ZenLiteDevice = None

ZenLiteSDK.set_log_level(LogLevel.warning)

class DeviceListener(ZenLiteDeviceListener):
    def on_connectivity_change(self, connectivity):
        ZLOG.LOG_WARNING("Connectivity: " + connectivity.name)
        if connectivity == Connectivity.connected:
            _target_device.zl_pair(_target_device.in_pairing_mode, self.on_pair_response)

    def on_contact_state_change(self, contact_state):
        ZLOG.LOG_WARNING("Contact state: " + contact_state.name)

    def on_orientation_change(self, orientation):
        ZLOG.LOG_WARNING("orientation:" + orientation.name)

    def on_sleep_stage(self, stage, conf, drowsiness):
        conf = round(conf, 1)
        drowsiness = round(drowsiness, 1)
        ZLOG.LOG_INFO("stage: " + str(stage)+ ", conf: " + str(conf) + ", drowsiness: " + str(drowsiness) + ", awareness: " + str(100 - drowsiness))
        
    def on_meditation(self, meditation, calmness, awareness):
        meditation = round(meditation, 1)
        calmness = round(calmness, 1)
        awareness = round(awareness, 1)
        ZLOG.LOG_INFO("Meditation: " + str(meditation) + ", calmness: " + str(calmness) + ", awareness: " + str(awareness))

    def on_eeg_data(self, eeg_data):
        pass

    def on_brain_wave(self, brain_wave):
        pass

    def on_imu_data(self, imu_data):
        pass

    def on_ppg_data(self, ppg_data):
        pass

    def on_afe_response(self, device, res):
        print(f"[{device.name}], on_afe_response:", res.success())

    def on_imu_response(self, device, res):
        print(f"[{device.name}], on_imu_response:", res.success())

    def on_ppg_response(self, device, res):
        print(f"[{device.name}], on_ppg_response:", res.success())

    def on_sleep_response(self, device, res):
        print(f"[{device.name}], on_sleep_response:", res.success())

    def on_pair_response(self, device, res):
        print(f"[{device.name}], on_pair_response:", res.success())
        if not res.success():
            return

        # time.sleep(0.1)
        ZLOG.LOG_INFO("start subscribe EEG")
        _target_device.zl_config_afe(EEGSampleRate.sr256, self.on_afe_response)

        ZLOG.LOG_INFO("start subscribe IMU")
        _target_device.zl_config_imu(IMUSampleRate.sr50, IMUMode.acc_gyro, self.on_imu_response)

        # 连续的心率+血氧检测
        ZLOG.LOG_INFO("start subscribe PPG, Continuous HR & SpO2 detection")
        _target_device.zl_config_ppg(PPGReportRate.sr25, PPGMode.algo, 0, 2000, self.on_ppg_response)


def on_found_device(device):
    print(f"Found device, address={device.addr}, name={device.name}, pairing_mode={device.in_pairing_mode}, battery_level={device.battery_level}")

    if device.name == _TARGET_DEVICE_NAME:
        global _target_device
        # print("Found %d devices" % len(devices))
        ZLOG.LOG_INFO("Stop scanning for more devices")
        ZenLiteSDK.stop_scan()
        _target_device = device
        _target_device.set_listener(DeviceListener())
        _target_device.connect()


if __name__ == "__main__":
    try:  
        ZenLiteSDK.start_scan(on_found_device)
        time.sleep(_TOTAL_RUN_SECONDS)  # 6 minutes before timeout
        ZLOG.LOG_ERROR("Timeout, disposing")
    except KeyboardInterrupt:
        ZLOG.LOG_ERROR("Early termination from keyboard")

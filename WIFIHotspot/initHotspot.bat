#!/bin/bash
# 树莓派5热点自动配置脚本 (create_ap版).
# 使用方法：sudo ./setup_hotspot.sh

# 检查root权限
if [ "$(id -u)" -ne 0 ]; then
  echo "请使用sudo运行此脚本！"
  exit 1
fi

# 配置参数（按需修改）
WIFI_IFACE="wlan0"             # 无线网卡名称
INTERNET_IFACE="eth0"          # 有线上网网卡
SSID="RPi5_Hotspot"            # 热点名称
PASSWORD="tanlihua"        # 密码（至少8位）
CHANNEL="149"                    # 推荐信道（避免冲突）
GATEWAY="10.0.0.1"             # 热点网关IP
FREQ_BAND="5"                  # 频段：2.4或5GHz（树莓派5支持5GHz）


# 创建配置文件
echo "[3/4] 生成配置文件..."
cat << EOF > /etc/create_ap.conf
CHANNEL=default
GATEWAY=10.0.0.1
WPA_VERSION=2
ETC_HOSTS=0
DHCP_DNS=gateway
NO_DNS=0
NO_DNSMASQ=0
HIDDEN=0
MAC_FILTER=0
MAC_FILTER_ACCEPT=/etc/hostapd/hostapd.accept
ISOLATE_CLIENTS=0
SHARE_METHOD=nat
IEEE80211N=0
IEEE80211AC=0
HT_CAPAB=[HT40+]
VHT_CAPAB=
DRIVER=nl80211
NO_VIRT=0
COUNTRY=
FREQ_BAND=2.4
NEW_MACADDR=
DAEMONIZE=0
NO_HAVEGED=0
WIFI_IFACE=wlan0
INTERNET_IFACE=eth0
SSID=$SSID
PASSPHRASE=$PASSWORD
USE_PSK=0
EOF

# 创建启动脚本
echo "[4/4] 创建启动服务..."
cat << EOF > /usr/local/bin/start_hotspot.sh
#!/bin/bash
# 关闭省电模式（树莓派5专属优化）
iwconfig $WIFI_IFACE power off

# 停止冲突服务
systemctl stop wpa_supplicant 2>/dev/null
ifconfig $WIFI_IFACE down

# 启动热点
create_ap --config /etc/create_ap.conf
EOF

chmod +x /usr/local/bin/start_hotspot.sh

# 创建Systemd服务
cat << EOF > /etc/systemd/system/rpi-hotspot.service
[Unit]
Description=Raspberry Pi 5 Hotspot Service
After=network.target

[Service]
ExecStart=/usr/local/bin/start_hotspot.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
systemctl daemon-reload
systemctl enable rpi-hotspot.service

echo "----------------------------------------"
echo "热点配置完成！"
echo "SSID: $SSID | 密码: $PASSWORD | 网关: $GATEWAY"
echo "启动热点: sudo systemctl start rpi-hotspot.service"
echo "查看状态: systemctl status rpi-hotspot.service"
echo "----------------------------------------"
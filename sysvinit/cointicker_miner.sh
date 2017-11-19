#! /bin/sh
# /etc/init.d/cointicker_miner

case "$1" in
  start)
    echo "Starting CoinTicker"
    # run application you want to start
    python /opt/coin-ticker/TickerDisplay_Miner.py >> /var/log/cointicker_miner.log 2>&1 &
    ;;
  stop)
    echo "Stopping Cointicker"
    # kill application you want to stop
    killall python
    ;;
  *)
    echo "Usage: /etc/init.d/cointicker_miner {start|stop}"
    exit 1
    ;;
esac

exit 0

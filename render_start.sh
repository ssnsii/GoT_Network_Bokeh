# Ensure the Bokeh server binds to all IPs and the correct port
bokeh serve main.py \
  --allow-websocket-origin=$RENDER_EXTERNAL_HOSTNAME \
  --port $PORT \
  --address 0.0.0.0

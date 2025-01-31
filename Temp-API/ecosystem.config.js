module.exports = {
    apps: [
      {
        name: "cpu-temp-api",
        script: "server.js",
        instances: "max", // Run multiple instances based on CPU cores
        exec_mode: "cluster", // Cluster mode for better performance
        autorestart: true,
        watch: false, // Change to true if you want it to restart on file changes
        max_memory_restart: "300M"
      }
    ]
  };
  
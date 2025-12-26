<template>
  <div class="notification-container">
    <div v-for="(notif, index) in notifications" :key="index" class="holder">

      <div :class="['notification', notif.type]">

        <pre
          style="text-wrap: auto; text-align: right; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; font-size: 0.8em; margin: 0px; margin-top:10px;">
      {{ notif.message }}
    </pre>

      </div>
    </div>
  </div>


  <div v-if="showGettingStarted">
    <div class="createfirst" style="" id="createCert">

      <div class="holder" style="margin: 10px; height: calc(100% - 40px);">

        <p class="createfirst"
          style="font-size: 1.2em; font-weight: 300; text-transform: uppercase; margin-top: 5px; margin-bottom: 5px;">
          👋 Get started
        </p>
        <p class="createfirst" style="margin-top: 5px;">You don't have any certificate authorities yet. Click below to
          get started</p>
          <hr>

        <div style="display: flex; justify-content: center; margin-top: 20px;">
          <button class="glass-button" style="width: 200px; height: 2.5em; margin-bottom: 20px;"
            @click="showGettingStarted = false; $router.push({ path: '/createcert', query: { show: 'ca' } })">
            Set one up ➜
          </button>
        </div>
      </div>

    </div>
  </div>

</template>

<script>
  import emitter from '@/eventBus';
  let nextId = 1; // unique id for each notification
  export default {
    name: 'NotificationPopup',
    data() {
      return {
        notifications: [],
        showGettingStarted: false
      };
    },
    methods: {
      /**
       * Add a notification
       * type: 'error' or 'warning'
       * message: string
       */
      addNotification(type, message) {

        if (type == "success") { message = `✅ ${message}`}
        if (type == "error") { message = `⛔ ${message}`}
        if (type == "warning") { message = `⚠️ ${message}`}


 
        const notif = {
          id: nextId++,
          type,
          message
        };
        this.notifications.push(notif);

        // Remove automatically after 10s for errors, 5s for warnings
        const timeout = type === 'error' ? 10000 : 5000;
        setTimeout(() => {
          this.notifications = this.notifications.filter(n => n.id !== notif.id);
        }, timeout);
      }
    },
    // Add handler for notification. Previously called function directly. 
    async mounted() {
      emitter.on('notificationContent', (payload) => {
        let type = payload.type
        let content = payload.content
        this.addNotification(type, content)
      })


      emitter.on('notificationGetStarted', (payload) => {
        console.log(payload)
        this.showGettingStarted = true
        setTimeout(() => {
          this.showGettingStarted = false
        }, 9000);
      })
    }
  };
</script>

<style scoped>
  div.holder {
    text-align: left;
    border-radius: 10px;
    width: -webkit-fill-available;
    /* Thicker, smoother liquid glass base */
    background: linear-gradient(145deg,
        rgba(61, 60, 60, 0.791),
        rgba(173, 173, 174, 0.693),
        rgba(255, 182, 193, 0.05));
    background-size: 200% 200%;
    animation: liquidShift 12s ease infinite;

    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);

    border: 1px solid rgba(255, 255, 255, 0.35);
    box-shadow:
      inset 0 0 10px rgba(255, 255, 255, 0.3),
      0 8px 32px rgba(0, 0, 0, 0.25);
  }

  .notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 300px;
    z-index: 999999;
  }

  .notification {
    padding: 12px 20px;
    border-radius: 6px;
    color: #fff;
    animation: slideIn 0.3s ease-out;

  }

  div.notification {
    margin-left: 10px;
    margin-right: 10px;
  }


  /* Error style */
  .notification.error {


    background: linear-gradient(145deg,
        rgba(152, 149, 149, 0.806),
        rgba(207, 207, 219, 0.693),
        rgba(255, 182, 193, 0.05));
    background-size: 200% 200%;
    animation: liquidShift 12s ease infinite;

    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);

    box-shadow:
      inset 0 0 10px rgba(255, 255, 255, 0.3),
      0 8px 32px rgba(0, 0, 0, 0.25);


    /* Subtle borders */
    border: 1px solid rgba(198, 1, 1, 0.325);

    /* Optional shadow for depth */
    box-shadow: 0 4px 30px rgba(198, 1, 1, 0.1);
  }

  /* Warning style */
  .notification.warning {

    background: linear-gradient(145deg,
        rgba(255, 255, 255, 0.25),
        rgba(180, 220, 255, 0.08),
        rgba(255, 182, 193, 0.05));
    background-size: 200% 200%;
    animation: liquidShift 12s ease infinite;

    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);

    box-shadow:
      inset 0 0 10px rgba(255, 255, 255, 0.3),
      0 8px 32px rgba(0, 0, 0, 0.25);

    backdrop-filter: blur(12px) saturate(180%);
    /* Subtle borders */
    border: 1px solid rgba(198, 113, 1, 0.325);

    /* Optional shadow for depth */
    box-shadow: 0 4px 30px rgba(198, 113, 1, 0.1);
  }

  /* Warning style */
  .notification.success {

    background: linear-gradient(145deg,
        rgba(255, 255, 255, 0.25),
        rgba(180, 220, 255, 0.08),
        rgba(255, 182, 193, 0.05));
    background-size: 200% 200%;
    animation: liquidShift 12s ease infinite;

    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);

    box-shadow:
      inset 0 0 10px rgba(255, 255, 255, 0.3),
      0 8px 32px rgba(0, 0, 0, 0.25);

    backdrop-filter: blur(12px) saturate(180%);
    /* Subtle borders */
    border: 1px solid rgba(1, 198, 17, 0.325);

    /* Optional shadow for depth */
    box-shadow: 0 4px 30px rgba(198, 113, 1, 0.1);
  }

  div.createfirst {

    position: absolute;
    bottom: 10px;
    right: 0;
    width: 300px;
    height: 230px;
    margin-right: 10px;
    border-radius: 15px;


    /* Thicker, smoother liquid glass base */
    background: linear-gradient(145deg,
        rgba(61, 60, 60, 0.791),
        rgba(173, 173, 174, 0.693),
        rgba(255, 182, 193, 0.05));
    background-size: 200% 200%;
    animation: liquidShift 12s ease infinite;

    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);

    border: 1px solid rgba(255, 255, 255, 0.35);
    box-shadow:
      inset 0 0 10px rgba(255, 255, 255, 0.3),
      0 8px 32px rgba(0, 0, 0, 0.25);
    ;

    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;

    z-index: 9999;

  }

  div.holder {

    /* Thicker, smoother liquid glass base */
    background: linear-gradient(145deg,
        rgba(255, 255, 255, 0.25),
        rgba(180, 220, 255, 0.08),
        rgba(255, 182, 193, 0.05));
    background-size: 200% 200%;
    animation: liquidShift 12s ease infinite;

    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);

    border: 1px solid rgba(255, 255, 255, 0.35);
    box-shadow:
      inset 0 0 10px rgba(255, 255, 255, 0.3),
      0 8px 32px rgba(0, 0, 0, 0.25);


    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
  }


  p.createfirst {
    text-align: left;
    margin-left: 10px;
    margin-right: 10px;
  }


  .glass-button {
    padding: 9.5px 20px;
    border-radius: 5px;
    font-size: 16px;
    font-weight: 500;
    color: #fff;
    /* White text works best on glass */
    cursor: pointer;
    text-align: center;

    /* Thicker, smoother liquid glass base */
    background: linear-gradient(145deg,
        rgba(255, 255, 255, 0.654),
        rgba(180, 220, 255, 0.08),
        rgba(255, 182, 193, 0.05));
    background-size: 200% 200%;
    animation: liquidShift 12s ease infinite;

    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);

    border: 1px solid rgba(255, 255, 255, 0.671);
    box-shadow:
      inset 0 0 10px rgba(255, 255, 255, 0.3),
      0 8px 32px rgba(0, 0, 0, 0.25);
  }

  /* Hover effect */
  .glass-button:hover {
    background: rgba(255, 255, 255, 0.25);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.25);
  }

  /* Active / pressed */
  .glass-button:active {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(0);
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.2);
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(100%);
    }

    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
</style>
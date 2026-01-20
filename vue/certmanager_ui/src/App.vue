<template>
    <NotificationPopup></NotificationPopup>

  <div style="z-index: 100; position:fixed; top: 55px; width: 100%;" v-show="this.isLoading">
  
  
    <HorizontalLoader></HorizontalLoader>
    </div>
  <nav v-if="!$route.meta.hideNavbar">
    <!-- LEFT -->
    <div class="left">
      <router-link to="/">ꄗ CRTMGR</router-link>
      <router-link to="/tree">CERT RELATIONS</router-link>
    </div>



    <!-- RIGHT -->
    <div class="right">
      <a ref="additional_settings_btn" @click="toggleOpen" to="#">
        ☰
      </a>
    </div>

    <!-- Animate dropdown -->
    <transition name="dropdown">
      <div v-if="open" class="additional_settings" ref="additional_settings">
        <div class="holder1">
          <p style="margin:0; margin-left: 5px; margin-right: 5px;">{{ current_time }}</p>
          <p style="margin:0; margin-left: 5px; margin-right: 5px;">Hello, {{ username }}</p>

          <br>
          <router-link style="display: block; text-align: left; background: linear-gradient(to bottom right,
              rgba(255, 255, 255, 0.6),
              rgba(255, 255, 255, 0) 70%); margin-bottom: 5px;" to="/settings">
            <img class="icon" src="/icons/gear.png">&nbsp;SETTINGS
          </router-link>

          <router-link style="display: block; text-align: left; background: linear-gradient(to bottom right,
              rgba(255, 255, 255, 0.6),
              rgba(255, 255, 255, 0) 70%); margin-bottom: 5px;" to="/apidocs">
            <img class="icon" src="/icons/attachment.png">&nbsp;API DOCS
          </router-link>

          <router-link style="display: block; text-align: left; background: linear-gradient(to bottom right,
              rgba(255, 255, 255, 0.6),
              rgba(255, 255, 255, 0) 70%)" to="/login" v-on:click="logout">
            <img class="icon" src="/icons/motion_blur.png">&nbsp;LOGOUT
          </router-link>
        </div>
      </div>
    </transition>
  </nav>

  <!-- Animate route changes -->
  <transition name="page" mode="out-in">
    <router-view />
  </transition>

  <ApiConnect ref="ApiConnect" />

  <div :class="{ hidden: !isLoading }" id="follower">
    <LoadingIcon style="height: 20px; width: 20px;" />

  </div>
</template>




<script>
  import ApiConnect from './components/ApiConnect.vue';
import HorizontalLoader from './components/assets/HorizontalLoader.vue';
  import LoadingIcon from './components/assets/LoadingIcon.vue'
  import emitter from './eventBus.js';
  import NotificationPopup from './components/NotificationPopup.vue';

  export default {
    name: 'App',
    components: {
      LoadingIcon,
      ApiConnect,
      HorizontalLoader, 
      NotificationPopup
    },
    data() {
      return {
        current_time: new Date().toLocaleTimeString(),
        isLoading: false,
        username: "somebody",
        open: false
      }
    },
    methods: {
      logout: function() {
        localStorage.removeItem('crtmgr-jwt')
      },
 
      toggleOpen: function () {
        this.open = !this.open
      },
      initMouseFollower: function () {
        const follower = document.getElementById("follower");

        document.addEventListener("mousemove", (e) => {
          follower.style.left = e.pageX + 10 + "px";
          follower.style.top = e.pageY + 10 + "px";
        })

      },
      handleClickOutside: function (event) {
        const additionalSettings = this.$refs.additional_settings;
        const additionalSettingsBtn = this.$refs.additional_settings_btn
        if (
          (additionalSettings &&
            !additionalSettings.contains(event.target)) && (additionalSettingsBtn && !additionalSettingsBtn
            .contains(
              event.target))

        ) {
          console.log("click outside")
          this.open = false;
        }

      }
    },
    async mounted() {
      // handle looking for click out
      document.addEventListener('click', this.handleClickOutside);
      this.initMouseFollower()

      // Update every second
      this.username = this.$refs.ApiConnect.get_jwt()['sub']
      this.current_time = setInterval(() => {
        this.current_time = new Date().toLocaleTimeString()
      }, 1000)

      emitter.on('loadingContent', (payload) => {
        this.isLoading = payload;
      })
    },
    beforeUnmount() {
      // Clean up to avoid memory leaks
      clearInterval(this.timer)
      document.removeEventListener('click', this.handleClickOutside);
    }
  }
</script>

<style>
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #d1cfcf;
  }

  nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    /* spread left, center, right */
        background: linear-gradient(to bottom right,
        rgba(22, 163, 233, 0.6),
        rgba(255, 255, 255, 0) 55%);
        padding: 10px;
        height: 40px;

  }

  nav .holder {
    display: flex;
    align-items: center;
    gap: 10px;
    /* spacing between children */
  }

  .center {
    display: flex;
    align-items: center;
    /* vertical centering */
    gap: 10px;
    /* spacing between time + icon */
  }



  div.holder {
    text-align: left;
    border-radius: 10px;
    /* Apple Glassmorphism base */
    background: linear-gradient(to bottom right,
        rgba(255, 255, 255, 0.6),
        rgba(255, 255, 255, 0) 70%);
    width: fit-content;
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);

    /* Subtle borders */
    border: 1px solid rgba(255, 255, 255, 0.3);

    /* Optional shadow for depth */
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);

    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
    padding-top: 10px;
    padding-bottom: 10px;
    margin-top: 10px;
    display: inline-block;
  }


  p.holder {
    display: inline-block;
    margin: 0;
    vertical-align: middle;
    line-height: 1;
    /* keeps it snug */
  }

  nav a {
    font-weight: bold;
    color: white;
    vertical-align: middle;
    text-decoration: none;
    padding: 10px;
    border-radius: 5px;
    font-weight: 300;

    border-radius: 5px;
    font-size: 16px;
    font-weight: 500;
    color: #fff;
    /* White text works best on glass */
    cursor: pointer;
    text-align: center;

    /* Glass background */

    /* Frosted border */

    /* Glow */

    /* Smooth transition */
    transition: all 0.3s ease;

  }

  nav a:hover {
    background: rgba(255, 255, 255, 0.25);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.25);


  }

  nav a.router-link-exact-active {
    color: white;
    font-weight: 600;
    animation: cyber-glow 10.5s infinite alternate;

  }

  /* Add a “glitching code” effect */
  @keyframes cyber-glow {

    0%,
    100% {
      text-shadow: 0 0 5px rgb(213, 213, 213), 0 0 10px rgb(210, 210, 210);
    }

    50% {
      text-shadow: 0 0 7px rgb(181, 181, 181), 0 0 20px rgb(198, 198, 198);
    }
  }

  .glitched {
    font-size: 1em;
    color: rgb(232, 234, 232);
    animation: cyber-glow 10.5s infinite alternate;
  }

  div.additional_settings {
    position: absolute;
    top: 70px;
    right: 10px;
    height: 25vh;
    width: 200px;
    z-index: 30;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);

    /* Subtle borders */
    border: 1px solid rgba(255, 255, 255, 0.3);

    /* Optional shadow for depth */
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);

    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
    padding: 10px;
    padding-left: 7px;
    padding-right: 7px;
    padding-bottom: 7px;
    border-radius: 10px;
  }


  div.holder1 {
    height: calc(25vh - 30px);
    text-align: left;
    border-radius: 10px;
    width: -webkit-fill-available;
    /* Apple Glassmorphism base */
    background: linear-gradient(145deg,
        rgba(61, 60, 60, 0.791),
        rgba(173, 173, 174, 0.693),
        rgba(255, 182, 193, 0.05));
            background-size: 200% 200%;

    backdrop-filter: blur(90px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);

    /* Subtle borders */
    border: 1px solid rgba(255, 255, 255, 0.3);

    /* Optional shadow for depth */
    box-shadow: -12px 11px 30px 8px rgba(0, 0, 0, 0.2);
    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
    padding: 10px;
    margin-top: 5px;
    color: white;
  }

  div.holder1::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: rgba(214, 205, 205, 0.429);
    /* Dark tint */
    pointer-events: none;
  }

  img.icon {
    height: 20px;
    vertical-align: middle;
  }

  /* ROUTE PAGE TRANSITION */
  .page-enter-active,
  .page-leave-active {
    transition: all 0.4s ease;
  }

  .page-enter-from {
    opacity: 0;
    transform: translateY(15px);
  }

  .page-enter-to {
    opacity: 1;
    transform: translateY(0);
  }

  .page-leave-from {
    opacity: 1;
    transform: translateY(0);
  }

  .page-leave-to {
    opacity: 0;
    transform: translateY(-15px);
  }

  /* DROPDOWN ANIMATION */
  .dropdown-enter-active,
  .dropdown-leave-active {
    transition: all 0.3s ease;
  }

  .dropdown-enter-from,
  .dropdown-leave-to {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }

  .dropdown-enter-to,
  .dropdown-leave-from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }

  .hidden{
    display: none;
  }

  #follower {
  position: fixed;       /* allows left/top to move it */
  left: 0;
  top: 0;
  pointer-events: none;  /* so it doesn’t block clicks */
  z-index: 9999;
}

.hide-cursor {
  cursor: none;
}
</style>
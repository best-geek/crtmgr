<template>
  <div class="login-container">
    <div class="pictureframe">
      <img v-if="!this.isLoading" style="margin-left: auto; margin-right: auto; text-align: center; width: 75px;"
        src="/icons/icon.png" />
      <LoadingIcon style="margin-left: auto; margin-right: auto; text-align: center; margin-top: 25px"
        v-if="this.isLoading" />

    </div>

    <h1 style="font-weight: 100;">ꄗ CRTMGR</h1>

    <input v-model="this.username" type="text" id="username" name="username" placeholder="USERNAME"><br><br>
    <input @keyup.enter="do_login" v-model="this.password" type="password" id="password" name="password"
      placeholder="PASSWORD" required><br><br>
    <button class="glass-button" :onclick="do_login">Login </button>

    <p v-show="this.err" style="color: red;">{{ this.err }}</p>
    <p v-show="!this.err" style="color: whitesmoke;">Login to continue</p>


  </div>
  <ApiConnect ref="ApiConnect" />

</template>

<script>
  import ApiConnect from './components/ApiConnect.vue';
  import LoadingIcon from './components/assets/LoadingIcon.vue';
  import emitter from './eventBus.js';


  export default {
    name: 'LogonWindow',
    components: {
      ApiConnect,
      LoadingIcon
    },
    data() {
      return {
        username: "",
        password: "",
        err: "",
        isLoading: false
      }
    },
    methods: {
      async do_login() {
        localStorage.removeItem("crtmgr-jwt") // remove old token

        const payload = {
          "username": this.username,
          "password": this.password
        }
        var response = await this.$refs.ApiConnect.send_post("/user/login/", payload)
        console.log(response)
        if (response.errors.length > 0) {
          this.err = response.errors.join("<br>")
        }

        if (response.token != undefined && response.token.length > 0) {
          this.$router.push("/")
        }

      }
    },
    mounted() {
      emitter.on('loadingContent', (payload) => {
        this.isLoading = payload;
      })
    }
  }
</script>

<style scoped>
  div.login-container {
    position: absolute;
    top: 50%;
    right: 50%;
    transform: translate(50%, -50%);
  }

  input[type="text"],
  input[type="password"] {
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    color: white;

    background: linear-gradient(to bottom right,
        rgba(50, 50, 50, 0.35),
        rgba(30, 30, 30, 0.15));
    border: 1px solid rgba(255, 255, 255, 0.7);
    box-shadow:
      inset 0 0 10px rgba(255, 255, 255, 0.4),
      0 6px 28px rgba(0, 0, 0, 0.3);

  }

  input::placeholder,
  textarea::placeholder {
    color: white;
    opacity: 1;
    /* Some browsers (like Firefox) lower opacity by default */
  }


  .glass-button {
    padding: 15px 25px;
    border-radius: 5px;
    font-size: 0.9em;
    font-weight: 500;
    margin: 5px;
    color: #fff;
    /* White text works best on glass */
    cursor: pointer;
    text-align: left;


    background: linear-gradient(to bottom right,
        rgba(255, 255, 255, 0.35),
        rgba(255, 255, 255, 0.05));
    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);
    border: 1px solid rgba(255, 255, 255, 0.35);
    box-shadow:
      inset 0 0 6px rgba(255, 255, 255, 0.3),
      0 4px 25px rgba(0, 0, 0, 0.25);

    /* Smooth transition */
    transition: all 0.3s ease;
    vertical-align: middle;
  }



  .glass-button-selected {
    padding: 15px 25px;
    border-radius: 5px;
    font-size: 16px;
    font-weight: 500;
    margin: 5px;
    width: calc(100% - 10px);
    color: #fff;
    /* White text works best on glass */
    cursor: pointer;
    text-align: left;

    background: linear-gradient(to bottom right,
        rgba(50, 50, 50, 0.35),
        rgba(30, 30, 30, 0.15));
    border: 1px solid rgba(255, 255, 255, 0.7);
    box-shadow:
      inset 0 0 10px rgba(255, 255, 255, 0.4),
      0 6px 28px rgba(0, 0, 0, 0.3);

    /* Smooth transition */
    transition: all 0.3s ease;
    vertical-align: top;
  }

  /* Hover effect */
  .glass-button:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
    box-shadow:
      0 8px 28px rgba(0, 0, 0, 0.3),
      inset 0 0 10px rgba(255, 255, 255, 0.4);
  }


  div.pictureframe {
    border-radius: 15px;
    max-width: 50vw;
    height: 80px;
    width: 80px;
    padding: 10px;
    /* Apple Glassmorphism base */
    background: linear-gradient(to bottom right,
        rgba(255, 255, 255, 0.6),
        rgba(255, 255, 255, 0) 70%);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);

    /* Subtle borders */
    border: 3px solid rgba(255, 255, 255, 0.384);

    /* Optional shadow for depth */
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);

    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
    margin-top: 10px;
    margin-left: auto;
    margin-right: auto;
  }

  div.pictureframe::before {
    background: linear-gradient(to bottom right,
        rgba(255, 255, 255, 0.6),
        rgba(255, 255, 255, 0) 70%);
    transform: rotate(-10deg);
    position: absolute;
    width: 65%;
    height: 60%;

    transform: rotate(-10deg);

  }
</style>
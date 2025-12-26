<template>
  <div>
    <dialog id="setPassword" class="modal">
                <button autofocus class="close-btn" v-on:click="hideModal()">x</button>
                                            <h2>Change Password</h2>


        <div class="holder">
                            <br>

            <div style="text-align: center; margin-left: auto; margin-right: auto;">
                    <input @keyup.enter="do_login" v-model="this.currentPass" type="password" id="passwordold" name="password" placeholder="EXISTING PASSWORD"
      required><br>

                          <input style="margin-top: 2px;" v-on:input="checkStatus" v-model="this.newPass1" type="password" id="password1" name="password" placeholder="NEW PASSWORD"
      required><br>

                          <input v-on:input="checkStatus" v-model="this.newPass2" type="password" id="password" name="password2" placeholder="VERIFY NEW PASSWORD"
      required><br>

                    <p>{{ this.changeStatus  }}</p>

                    <button class="glass-button" @click="changePassword()">SAVE</button>

            </div>
        </div>
      </dialog>

  </div>
  <ApiConnect ref="ApiConnect" />
</template>

<script>
import ApiConnect from '../ApiConnect.vue';


export default {
  name: 'CreateApiKey',
  components:{ 
    ApiConnect
  },
  data(){
    return{
        currentPass:"",
        newPass1:"",
        newPass2:"",
        changeStatus:"",
    }

  },
  methods: {
    showModal: function() {
        console.log("showing password")
        var e = document.getElementById('setPassword')
        e.showModal()
    }, 

        hideModal: function() {
        console.log("hiding password")
        var e = document.getElementById('setPassword')
        e.close()
    },
    checkStatus: function () {
        if (this.newPass1 != this.newPass2) {
            this.changeStatus = "Password do not match"
            return false
        }
        return true
    },
    changePassword: async function () {
        if (this.checkStatus() == false) { return }

        var token = this.$refs.ApiConnect.get_jwt()
        var foruser=token['sub']


        const payload = {
          "password": this.currentPass,
          "new_password": this.newPass2
        }


        var response = await this.$refs.ApiConnect.send_post(`/user/resetpassword/${foruser}/`, payload, {}, false)
        
        if (response != undefined && "errors" in response && response['errors'].length > 0 ) {
            this.changeStatus = response['errors'][0]
        }
        
        if (response != undefined && "result" in response && response['result'] == true ) {
          this.changeStatus = "Changed password successfully."
        } else {
            this.changeStatus = "Error changing password."
        }



    }



  }
};
</script>


<style scoped>

  h2 {
    margin: 1px;
    text-transform: uppercase;
    font-weight: 400;

  }

h2:first-of-type {
    display: inline-block;
    vertical-align: middle;
        color: black;
    font-size: 0.8em;
    text-shadow: 0 0 20px rgb(248, 248, 248)
  }


.modal {
    text-align: left;
    border-radius: 15px;
    max-width: 50vw;
    min-width: 400px;
  /* Thicker, smoother liquid glass base */
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.25),
    rgba(180, 220, 255, 0.08),
    rgba(255, 182, 193, 0.05)
  );
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
    padding: 10px;
    padding-left: 7px;
    padding-right: 7px;
    padding-bottom: 7px;
  }

/* 🔥 This styles the dim background when the dialog is open */
::v-deep(dialog::backdrop) {
  background: rgba(0, 0, 0, 0.6); /* semi-transparent black */
      backdrop-filter: blur(5px) saturate(180%);

}


div.holder {
    text-align: left;
    border-radius: 10px;
    max-width: 50vw;
    min-width: 400px;
    width: -webkit-fill-available;
  /* Thicker, smoother liquid glass base */
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.25),
    rgba(180, 220, 255, 0.08),
    rgba(255, 182, 193, 0.05)
  );
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
    padding: 10px;
    margin-top: 10px;
}

/* Container */
.close-btn {
  position: absolute;
  top: 0;
  right: 10px;
    padding: 3px 20px;
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;

    font-size: 13px;
    font-weight: 500;
    color: #fff;
    /* White text works best on glass */
    cursor: pointer;
    text-align: center;

    /* Glass background */
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);

    /* Frosted border */
    border: 1px solid rgba(255, 255, 255, 0.3);

    /* Glow */
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

    /* Smooth transition */
    transition: all 0.3s ease;
}

.close-btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 65%;
  height: 60%;
  background: linear-gradient(
    to bottom right,
    rgba(255,255,255,0.6),
    rgba(255,255,255,0) 70%
  );
  transform: rotate(-10deg);
  pointer-events: none;
}

.close-btn:hover {
  background: linear-gradient(to bottom, #f63434, #cc000061);
  color: wheat;
}

  img.header-icon{
    height: 30px;
    margin-bottom: 10px;
    vertical-align: middle;
    display: inline-block;
    vertical-align: middle;
    margin-left: 10px;
    margin-right: 5px;
  }

  input[type="text"],
  input[type="password"],
  input[type="number"] {
    padding: 5px 20px;
    border-radius: 5px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    color: white;
    min-width: 300px;
    margin-bottom: 10px;


 background: linear-gradient(
    to bottom right,
    rgba(50, 50, 50, 0.35),
    rgba(30, 30, 30, 0.15)
  );
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow:
    inset 0 0 10px rgba(255, 255, 255, 0.4),
    0 6px 28px rgba(0, 0, 0, 0.3);

  }
  input::placeholder,
textarea::placeholder {
  color: white;
  opacity: 1; /* Some browsers (like Firefox) lower opacity by default */
}


   .glass-button {
    padding: 9.5px 20px;
    border-radius: 5px;
    font-size: 16px;
    font-weight: 500;
    margin: 5px;
    color: #fff;
    /* White text works best on glass */
    cursor: pointer;
    text-align: left;


  background: linear-gradient(
    to bottom right,
    rgba(255, 255, 255, 0.35),
    rgba(255, 255, 255, 0.05)
  );
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

</style>

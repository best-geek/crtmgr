<template>
  <div>
    <dialog id="apiKeyCreate" class="modal">
      <button autofocus class="close-btn" v-on:click="hideModal()">x</button>
      <h2>Create API Key</h2>


      <div class="holder">
        <br>

        <div style="text-align: left; margin-right: auto; padding: 10px;">
          <p style="">Create an API key. Note that permissions cannot be changed after creation.</p>
          <DropDownCheckbox style="text-align: left;" :options="this.permissionsOpts" :already_selected="[]"
            v-model="this.selectedPerms" placeholder="Select permissions"></DropDownCheckbox>
          <input class="short-input" v-model="this.valid_days" type="number"
            style="text-align: left; margin-top: 10px; width: 30px;" placeholder="Validity Days" />
          <br>
          <br>

          <input v-model="this.apiKey" type="text" id="apikey" name="apikey" placeholder="Generate Key"
            style="font-family: monospace; width: 300px; display: inline-block; vertical-align: middle;" readonly>

          &nbsp;
          <button style="display: inline-block; vertical-align: middle; margin-bottom: 10px;" class="glass-button"
            @click="copyValue()">Copy</button>
          <p>{{ this.changeStatus  }}</p>


        </div>




        <div style="text-align: center; margin-left: auto; margin-right: auto;">



          <button class="glass-button" @click="generateKey()">Create Key</button>

        </div>
      </div>
    </dialog>

  </div>
  <ApiConnect ref="ApiConnect" />
</template>

<script>
  import ApiConnect from '../ApiConnect.vue';
  import DropDownCheckbox from './DropDownCheckbox.vue';


  export default {
    name: 'ApiKeyCreate',
    components: {
      ApiConnect,
      DropDownCheckbox
    },
    data() {
      return {
        apiKey: "",
        changeStatus: ".",
        valid_days: null,
        selectedPerms: [],
        permissionsOpts: [{
            "displayName": "Inherit all permissions",
            "emitValue": "*"
          },
          {
            "displayName": "Read all certificate data",
            "emitValue": "read"
          },
          {
            "displayName": "Write certificate data",
            "emitValue": "write"
          },
          {
            "displayName": "Manage user information",
            "emitValue": "manage_users"
          },
        ]
      }

    },
    methods: {
      showModal: function () {
        console.log("showingApiKeyCreate")
        var e = document.getElementById('apiKeyCreate')
        e.showModal()
      },

      hideModal: function () {
        console.log("hidingApiKeyCreate")
        var e = document.getElementById('apiKeyCreate')
        e.close()
      },

      generateKey: async function () {


        const payload = {
          "roles": this.selectedPerms,
          "days_expiry": this.valid_days
        }


        var response = await this.$refs.ApiConnect.send_post(`/user/apikeys/create/`, payload, {}, false)

        if (response != undefined && "errors" in response && response['errors'].length > 0) {
          this.changeStatus = response['errors'][0]
        }

        if (response != undefined && "result" in response) {
          this.apiKey = response['result']['token']
          this.changeStatus = "This value will only be shown once."
        } else {
          this.changeStatus = "Error creating key"
        }



      },


      copyValue: function () {
        navigator.clipboard.writeText(this.apiKey)
          .then(() => {
            this.changeStatus = "Copied!";
          })
          .catch(err => {
            this.changeStatus = "Copy failed.";
            console.error(err);
          });
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
    min-height: 400px;
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
    background: rgba(0, 0, 0, 0.6);
    /* semi-transparent black */
    backdrop-filter: blur(0px) saturate(180%);

  }


  div.holder {
    text-align: left;
    border-radius: 10px;
    max-width: 50vw;
    min-height: 400px;
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
    background: linear-gradient(to bottom right,
        rgba(255, 255, 255, 0.6),
        rgba(255, 255, 255, 0) 70%);
    transform: rotate(-10deg);
    pointer-events: none;
  }

  .close-btn:hover {
    background: linear-gradient(to bottom, #f63434, #cc000061);
    color: wheat;
  }

  img.header-icon {
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
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    color: white;
    min-width: 255px;
    margin-bottom: 10px;


    /* Glass background */
    background: linear-gradient(to bottom right,
        rgba(255, 255, 255, 0.6),
        rgba(255, 255, 255, 0) 70%);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);

    /* Frosted border */
    border: 1px solid rgba(255, 255, 255, 0.3);

    /* Glow */
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

  }

  input::placeholder,
  textarea::placeholder {
    color: rgb(117, 117, 117);
    opacity: 1;
    /* Some browsers (like Firefox) lower opacity by default */
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

  input.short-input[type="number"] {
    min-width: unset !important;
    width: 120px !important;
  }
</style>
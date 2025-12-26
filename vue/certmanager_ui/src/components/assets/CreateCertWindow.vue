<template>
  <div style="text-align: center; width: 100%; margin-left: auto; margin-right: auto;">
    <h3>Certificate Metadata</h3>
    <input style="display: grid; margin-top: 10px; width: -webkit-fill-available;" v-model="this.certName" type="text"
      id="name" name="name" placeholder="New Certificate Name">

    <DropDown style="width: -webkit-fill-available; display: inline-flex;" v-model="this.selected_authority_sysid"
      :options="this.authorities_dropdown" placeholder="Select a parent certificate authority"></DropDown>
    <input style="display: grid; margin-top: 10px; width: -webkit-fill-available" v-model="this.keyphrase"
      type="password" id="password" name="password" placeholder="Certificate authority keyphrase">


    <div style=" text-align: left; margin-top: 10px; ">
      <input v-model="this.valid_days" type="number" style="text-align: left; margin-right: auto;"
        placeholder="Validity Days" />
    </div>

    <h3>Key Size</h3>
    <DropDown style="width: -webkit-fill-available; font-size: 1.0em; display: inline-flex;" v-model="this.keysize"
      :options="keysize_options" placeholder="Select keysize"></DropDown>




    <CertificateSubj style="display: grid" ref="CertificateSubj"></CertificateSubj>

    <button class="glass-button" v-on:click="createCert()">{{this.createButtontext}}</button>

  </div>
  <ApiConnect ref="ApiConnect" />
</template>

<script>
  import emitter from '@/eventBus'
  import ApiConnect from '../ApiConnect.vue'
  import CertificateSubj from './CertificateSubj.vue'
  import DropDown from './DropDown.vue'

  export default {
    name: 'CreateCertWindow',
    components: {
      ApiConnect,
      DropDown,
      CertificateSubj,
    },
    data() {
      return {
        authorities: [],
        authorities_dropdown: [],
        selected_authority_sysid: undefined,
        keyphrase: "",
        certName: "",
        valid_days: null,
        keysize_options: [{
            "emitValue": 2048,
            "displayName": "2048 bits"
          },
          {
            "emitValue": 3072,
            "displayName": "3072 bits"
          },
          {
            "emitValue": 4096,
            "displayName": "4096 bits"
          }
        ],
        keysize: 0,
        successfullyCreated: false,
        createButtontext: "Create"

      }
    },
    methods: {
      async get_authorities() {
        var response = await this.$refs.ApiConnect.send_get("/list/certauthority/", {}, true)
        if (response != undefined && "result" in response) {
          console.log(response)
          this.authorities = response.result
          return response.result
        }

      },
      populate_authority_dropdown(authorities) {
        authorities.forEach(element => {
          this.authorities_dropdown.push({
            "displayName": `Common Name: ${element.common_name}, Created: ${ this.unix_to_ts(element.created)}`,
            "emitValue": element.sys_id
          })

        });
      },
      unix_to_ts(unixTimestamp) {
        const date = new Date(unixTimestamp * 1000); // convert to milliseconds
        return date.toLocaleString();
      },
      async createCert() {

        if (this.successfullyCreated) {
          this.$refs.ApiConnect.download_certificate_buffered(this.selected_authority_sysid, this.certName)
          return
        }

        if (this.selected_authority_sysid == undefined) {
          emitter.emit('notificationContent', {"type":"error", "content":"A parent certificate authority must be selected"});

          return
        }


        if (this.certName == '') {
          emitter.emit('notificationContent', {"type":"error", "content":"A new certificate must have a name"});
          return
        }

        var payload = {
          "keyphrase": this.keyphrase,
          "name": this.certName,
          "cert_days_length": this.valid_days,
          "ca_name": this.authorities.filter((ca) => ca.sys_id == this.selected_authority_sysid)[0]['name'],
        }

        if (this.keysize > 0) {
          payload['keysize'] = this.keysize
        }

        var subjectData = this.$refs.CertificateSubj.returnPayload()
        var combinedPayload = {
          ...payload,
          ...subjectData
        }

        console.log(combinedPayload)

        var response = await this.$refs.ApiConnect.send_post(`/create/certificate/${this.selected_authority_sysid}/`,
          combinedPayload, {}, false)
        if (response != undefined && "result" in response && "cert" in response.result) {
          this.successfullyCreated = true
          this.createButtontext = "Download"
          this.$refs.ApiConnect.download_certificate_buffered(this.selected_authority_sysid, this.certName)
          this.$router.push("/")
        }


      }


    },
    mounted() {
      this.get_authorities().then((resp) => {
        this.populate_authority_dropdown(resp)
      })
    }
  }
</script>

<style scoped>
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
        margin-bottom: 5px;

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


  h3 {
    margin-bottom: 2px;
    text-align: left;
    text-transform: uppercase;
    color: white;
  }

  ::placeholder {
    color: white;
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
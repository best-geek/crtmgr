<template>
  <div style="text-align: center; width: 100%; margin-left: auto; margin-right: auto;">
    <h3>Certificate Metadata</h3>
    <input style="display: grid; margin-top: 10px; width: -webkit-fill-available;" v-model="this.certName" type="text" id="name" name="name"
      placeholder="New Certificate Authority Name">

    <input style="display: grid; margin-top: 10px; width: -webkit-fill-available" v-model="this.keyphrase" type="password" id="password" name="password"
      placeholder="Certificate Authority Keyphrase">


        <div style=" text-align: left; margin-top: 10px; ">
    <input v-model="this.valid_days" type="number" style="text-align: left; margin-right: auto;" placeholder="Validity Days" />
    </div>

    <h3>Key Size</h3>
        <DropDown style="width: -webkit-fill-available; font-size: 1.0em; display: inline-flex;" v-model="this.keysize" :options="keysize_options" placeholder="Select keysize"></DropDown>


    

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
    name: 'CreateCaWindow',
    components: {
      ApiConnect,
      DropDown,
      CertificateSubj,
    },
    data() {
      return {
        keyphrase: "",
        certName:"",
        valid_days:null,
        keysize_options: [
          {"emitValue":2048, "displayName":"2048 bits"},
          {"emitValue":3072, "displayName":"3072 bits"},
          {"emitValue":4096, "displayName":"4096 bits"}
        ],
        keysize:0,
        successfullyCreated:false,
        createdId:undefined,
        createButtontext:"Create"

      }
    },
    methods: {
        unix_to_ts(unixTimestamp) {
        const date = new Date(unixTimestamp * 1000); // convert to milliseconds
        return date.toLocaleString();
      },
      async createCert() {

        if (this.successfullyCreated){
          this.$refs.ApiConnect.download_authority_buffered(this.createdId)
          return
        }



        if (this.certName == '') {
          emitter.emit('notificationContent', {"type":"error", "content":"A new certificate must have a name"});
          return
        }

        var payload = {
          "keyphrase":this.keyphrase,
          "name":this.certName,
          "ca_days_length":this.valid_days,
        }
        
        if (this.keysize > 0) {
          payload['ca_keysize']=this.keysize
        }

        var subjectData = this.$refs.CertificateSubj.returnPayload()
        var combinedPayload = {...payload, ...subjectData}

        console.log(combinedPayload)

        var response = await this.$refs.ApiConnect.send_post('/create/certauthority/', combinedPayload,{},false)
        if (response != undefined && "result" in response && "id" in response.result) {
          this.successfullyCreated = true
          this.createdId = response['result']['id']
          this.createButtontext = "Download"
          this.$refs.ApiConnect.download_authority_buffered(this.createdId)
          this.$router.push("/")
        }


      }


    },
    mounted() {

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
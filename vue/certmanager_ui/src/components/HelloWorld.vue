<template>
  <ApiConnect ref="ApiConnect" />


  <div style="width: 88vw; margin-left: auto; margin-right: auto;">

    <br><br>

    <h2 style="text-align: left;">Manage Certificate Authorities</h2>
    <div class="table_container">
      <button v-on:click="$router.push({ path: '/createcert', query: { show: 'ca' } })" class="glass-button"
        style="margin-top: 5px; margin-left: 12px; float: left;"><img class="icon"
          src="/icons/add.png">&nbsp;New</button>
      <DropDown style=" margin-top: 5px; margin-left: 5px; float: left;" placeholder="Sort by"
        :options="this.certificateSortOpts" v-model="this.caFilterBy" @updateFilter="sortCertificates('ca')">
      </DropDown>
      <input v-model="this.caSearchterm" style="float: left; margin-top: 5px; margin-left: 5px;" type="text"
        id="filter_ca" name="filter_ca" placeholder="Search" @keyup="this.applySearch('ca')">

      <br>
      <br>
      <div class="table_container" style="margin: 10px; width: calc(100% - 20px);">
        <table cellpadding="8" cellspacing="0" class="table_container">
          <thead>
            <tr>
              <th>Common Name</th>
              <th>Name</th>
              <th>Created</th>
              <th>Status</th>
              <th>Remaining Days</th>
              <th>Days Lifetime</th>
              <th style="min-width: 15vw;">Action</th>
            </tr>
          </thead>
          <tbody>

            <tr v-for="ca in this.authorities_show" :key="ca.sys_id">
              <td style="font-weight: 500;">{{ ca.common_name }}</td>
              <td>{{ ca.name }}</td>
              <td>{{ unix_to_ts(ca.created) }}</td>
              <td v-bind:class="ca.status">{{ ca.status }}</td>
              <td>{{ ca.remaining_days }}</td>
              <td>{{ ca.days }}</td>
              <td>
                <button class="glass-button" @click="showDeleteModal('ca',ca.sys_id)"
                  style="margin-right: 5px; padding: 5px;"><img class="icon" src="/icons/delete.png"></button>
                <button class="glass-button" @click="$refs.ApiConnect.download_authority_buffered(ca.sys_id)"
                  style="margin-right: 5px; padding: 5px;"><img class="icon" src="/icons/diskette.png"></button>
                <button class="glass-button" style="padding: 5px;" @click="showCaModal(ca.sys_id)"><img class="icon"
                    src="/icons/zoom.png"></button>
              </td>
            </tr>

          </tbody>
        </table>
      </div>


      <dialog id="viewCaModal" class="homeModal">
        <button autofocus class="close-btn" v-on:click="hideCaModel">x</button>

        <h2 class="modalhead">Certificate data</h2>
        <div class="holder">

          <pre style="text-wrap:initial;white-space: pre-line;font-size: 0.7em   "> {{ this.caModal_cert }} </pre>
        </div>
      </dialog>


    </div>

    <br><br>

    <h2 style="text-align: left;">Manage Certificates</h2>

    <div class="table_container">
      <button v-on:click="$router.push({ path: '/createcert', query: { show: 'cert' } })" class="glass-button"
        style="margin-top: 5px; margin-left: 12px; float: left;"><img class="icon"
          src="/icons/add.png">&nbsp;New</button>
      <DropDown style=" margin-top: 5px; margin-left: 5px; float: left;" placeholder="Sort by"
        :options="this.certificateSortOpts" v-model="this.certFilterBy" @updateFilter="sortCertificates('cert')">
      </DropDown>
      <input v-model="this.certSearchterm" style="float: left; margin-top: 5px; margin-left: 5px;" type="text"
        id="filter_cert" name="filter_cert" placeholder="Search" @keyup="applySearch('cert')">


      <br>
      <br>
      <div class="table_container" style="margin: 10px; width: calc(100% - 20px);">
        <table cellpadding="8" cellspacing="0">
          <thead>
            <tr>
              <th>Common Name</th>
              <th>CA Common Name</th>
              <th>Name</th>
              <th>Created</th>
              <th>Status</th>
              <th>Remaining Days</th>
              <th>Days Lifetime</th>
              <th style="min-width: 15vw;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cert in this.certificates_show" :key="cert.id">
              <td style="font-weight: 500;">{{ cert.common_name }}</td>
              <td style="font-weight: 500;">{{ cert.ca_common_name }}</td>
              <td>{{ cert.name }}</td>
              <td>{{ unix_to_ts(cert.created) }}</td>
              <td v-bind:class="cert.status">{{ cert.status }}</td>
              <td>{{ cert.remaining_days }}</td>
              <td>{{ cert.days }}</td>
              <td style="min-width: 10vw;">
                <button class="glass-button" @click="showDeleteModal('cert', cert.parent_ca_sys_id, cert.name)"
                  style="margin-right: 5px; padding: 5px;"><img class="icon" src="/icons/delete.png"></button>
                <button class="glass-button"
                  @click="$refs.ApiConnect.download_certificate_buffered(cert.parent_ca_sys_id, cert.name)"
                  style="margin-right: 5px; padding: 5px;"><img class="icon" src="/icons/diskette.png"></button>
                <button class="glass-button" style="padding: 5px;"
                  @click="showCertModal(cert.parent_ca_sys_id, cert.name)"><img class="icon"
                    src="/icons/zoom.png"></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <dialog id="viewcertModal" class="homeModal">
      <button autofocus class="close-btn" v-on:click="hideCertModal">x</button>
      <h2 class="modalhead">Certificate and key data</h2>

      <div class="holder">

        <h2>Certificate data</h2>
        <pre
          style="text-wrap:initial;white-space: pre-line; font-size: 0.8em; text-align: left;   "> {{ this.crtModal_cert }} </pre>
        <br>
        <h2>Key data</h2>
        <pre
          style="text-wrap:initial;white-space: pre-line; font-size: 0.8em; text-align: left;   "> {{ this.crtModal_key }} </pre>
      </div>
    </dialog>



    <dialog id="deleteModal" class="homeModal">
      <button autofocus class="close-btn" v-on:click="hideModal('deleteModal')">x</button>
      <h2 class="modalhead">Confirmation!</h2>

      <div class="holder">

        <p style="margin: 10px; color: darkred;" v-if="this.deleteModaltype == 'ca'">This will delete this authority.
          This will also delete <b> {{ this.caDeleteModelCount }}</b> underlying certificates associated
          with the authority. <br><br><i> (This action does not revoke the authority itself and will be trusted for as
            long as the certificate is valid)</i> <br><br></p>
        <p style="margin:10px; color: darkred; padding-bottom: 20px;" v-if="this.deleteModaltype == 'cert' ">This will
          delete this certificate from the store. Only delete this if you have a copy or it is no longer needed.</p>
        <p style="margin:10px; color: green;"> {{ this.deleteShowMessage }}</p>
        <div style="text-align: center; margin-left: auto; margin-right: auto; padding-bottom: 10px;">
          <button style=" margin-left: auto; margin-right: auto;" class="glass-button" v-if="this.showDeleteContinue"
            autofocus v-on:click="deleteModalContinue">
            <img class="icon" src="/icons/trash_full.png" alt="">
            Delete Anyway</button>
        </div>
      </div>
    </dialog>


  </div>


</template>

<script>
  import emitter from '@/eventBus';
  import ApiConnect from './ApiConnect.vue';
  import DropDown from './assets/DropDown.vue';



  export default {
    name: 'HelloWorld',
    components: {
      ApiConnect,
      DropDown,
    },
    props: {
      msg: String
    },
    data() {
      return {
        authorities_show: [],
        authorities: [],
        certificates: [],
        certificates_show: [],
        certificateSortOpts: [{
            "displayName": "Expiring Soon",
            "emitValue": "expiring-soonest"
          },
          {
            "displayName": "Name (A-Z)",
            "emitValue": "name-asc"
          },
          {
            "displayName": "Name (Z-A)",
            "emitValue": "name-desc"
          },
          {
            "displayName": "Newest Created First",
            "emitValue": "newest-oldest"
          },
          {
            "displayName": "Oldest Created First",
            "emitValue": "oldest-newest"
          },
        ],
        // modal for viewing ca
        caModal_cert: "",
        // modal for viewing cert
        crtModal_cert: "",
        crtModal_key: "",
        // modal for deleting ca 
        deleteModaltype: "",
        caDeleteModelCount: -1,
        caDeleteModalSysid: "",
        deleteModalCertName: "",
        deleteShowMessage: "",
        showDeleteContinue: false,
        // control search values
        caSearchterm: "",
        certSearchterm: "",
        // control filter
        caFilterBy: "",
        certFilterBy: "",
      }
    },
    methods: {
      unix_to_ts(unixTimestamp) {
        const date = new Date(unixTimestamp * 1000); // convert to milliseconds
        return date.toLocaleString();
      },

      async get_authorities() {
        var response = await this.$refs.ApiConnect.send_get("/list/certauthority/", {}, true)
        if (response != undefined && "result" in response) {
          this.authorities = response.result
          this.authorities_show = response.result

          if (this.authorities.length == 0) {
            emitter.emit('notificationGetStarted', true)
          }

        }

      },

      async get_certificates() {
        var response = await this.$refs.ApiConnect.send_get("/list/certificates/", {}, true)
        if (response != undefined && "result" in response) {
          this.certificates = response.result
          this.certificates_show = response.result
        }
      },
      showCaModal: async function (caid) {
        console.log(caid)
        this.caModal_cert = ""
        var response = await this.$refs.ApiConnect.send_get("/download/certauthority/" + caid + "/", {}, true)
        this.caModal_cert = response.result.cert
        var e = document.getElementById('viewCaModal')
        e.showModal()
      },

      showDeleteModal: async function (type, caid, name) {
        console.log(name)
        this.showDeleteContinue = true
        this.dele

        this.deleteModaltype = type
        this.caDeleteModalSysid = caid
        this.deleteModalCertName = name
        this.deleteShowMessage = ''


        if (type == "ca") {
          this.caDeleteModelCount = 0

          this.certificates.forEach(cert => {
            if (cert.parent_ca_sys_id === this.caDeleteModalSysid) {
              this.caDeleteModelCount += 1;
            }
          })
        }

        // var response = await this.$refs.ApiConnect.send_get("/download/certauthority/" + caid + "/", {}, true)
        var e = document.getElementById('deleteModal')
        e.showModal()
      },

      async deleteModalContinue() {
        var response = {}

        if (this.deleteModaltype == "cert") {
          response = await this.$refs.ApiConnect.send_get(
            `/delete/certificate/${this.caDeleteModalSysid}/${this.deleteModalCertName}/`, {}, true, true)
        }

        if (this.deleteModaltype == "ca") {
          response = await this.$refs.ApiConnect.send_get(`/delete/certauthority/${this.caDeleteModalSysid}/`, {},
            true, true)
        }

        if (response != undefined && "result" in response) {
          if ("deleted_id" in response.result) {
            this.showDeleteContinue = false // stop user from resubmitting
            this.deleteShowMessage = "deleted successfully."

          }
        }

      },

      hideModal: function (id) {
        var e = document.getElementById(id)
        e.close()

        if (id == "deleteModal") {
          this.get_authorities()
          this.get_certificates()
        }
      },


      showCertModal: async function (caid, name) {
        console.log(caid, name)
        this.caModel_cert = ""
        var response = await this.$refs.ApiConnect.send_get("/download/certificate/" + caid + "/" + name +
          "/", {},
          true, true)
        this.crtModal_cert = response.result.cert
        this.crtModal_key = response.result.key
        var e = document.getElementById('viewcertModal')
        e.showModal()
      },

      hideCaModel: function () {
        var e = document.getElementById('viewCaModal')
        e.close()
      },

      hideCertModal: function () {
        var e = document.getElementById('viewcertModal')
        e.close()
      },

      applySearch: function (type) {
        let searchTerm = ""
        let searchAcross = []
        let results = []

        if (type === "cert") {
          searchTerm = this.certSearchterm
          searchAcross = this.certificates
        }

        if (type === "ca") {
          searchTerm = this.caSearchterm
          searchAcross = this.authorities
        }

        searchAcross.forEach(element => {

          if (element) {
            let unique_id = "-999999999999999999" // something default user is unlikely to search


            // must give a unique identifier. A cert type does not have one
            // but name + sys_id makes it so
            if (type == "ca") {
              unique_id = element.sys_id
            }
            if (type == "cert") {
              unique_id = `${element.name}_${element.parent_ca_sys_id}`
            }


            if (
              element.name.includes(searchTerm) ||
              element.common_name.includes(searchTerm) ||
              element.owner.includes(searchTerm) ||
              element.status.includes(searchTerm) ||
              unique_id.includes(searchTerm)
            ) {
              results.push(element) // actually collect matches
            }
          }
        })

        if (type === "cert") {
          this.certificates_show = results
        }
        if (type === "ca") {
          this.authorities_show = results
        }

      },

      sortCertificates: function (datasource) {

        let results = []
        let type = ""

        if (datasource === "cert") {
          results = [...this.certificates] // take full copy
          type = this.certFilterBy
        }

        if (datasource === "ca") {
          results = [...this.authorities] // take full copy  
          type = this.caFilterBy
        }

        console.log(datasource, this.certFilterBy)

        if (type === "name-asc") {
          results.sort((a, b) => a.name.localeCompare(b.name))
        }

        if (type === "oldest-newest") {
          results.sort((a, b) => a.created - b.created)
          console.log("sorted oldest newest")
        }

        if (type === "newest-oldest") {
          results.sort((a, b) => b.created - a.created)
        }

        if (type === "name-desc") {
          results.sort((a, b) => b.name.localeCompare(a.name))
        }

        if (type === "expiring-soonest") {
          results.sort((a, b) => a.remaining_days - b.remaining_days)
        }

        if (datasource === "cert") {
          this.certificates_show = results
        }

        if (datasource === "ca") {
          this.authorities_show = results
        }
      }


    },
    async mounted() {
      // fetch both in parallel, then wait for both to finish
      await Promise.all([
        this.get_certificates(),
        this.get_authorities()
      ])

      // must await the above before we can search
      if (this.$route.query.search) {
        this.certSearchterm = this.$route.query.search
        this.caSearchterm = this.$route.query.search
        this.applySearch("ca")
        this.applySearch("cert")
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  h3 {
    margin: 40px 0 0;
  }

  h2 {
    margin: 1px;
    text-transform: uppercase;
    font-weight: 400;
    color: white;
  }

  ul {
    list-style-type: none;
    padding: 0;
  }

  li {
    display: inline-block;
    margin: 0 10px;
  }

  a {
    color: #42b983;
  }

  button.home {
    padding: 10px;
    background-color: white;
    color: #3a0071;
    border-radius: 5px;
    border: solid 2px white;
  }

  button.home:hover {
    background-color: #d4d4d4a1;

  }

  table {
    margin: auto;
    margin-top: 10px;
    max-height: 5vh;
    width: 98%;
    border-collapse: separate;
    white-space: wrap;
    table-layout: fixed;
    border-radius: 10px;
    color: rgb(55, 55, 55);
    margin: 10px;
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

  }

  th {
    position: sticky;
    top: 0;
    background: #66656539;

    z-index: 1;
    margin: 10px;
    text-align: center;
  }

  tr {
    text-transform: uppercase;
    font-weight: 300;
  }

  th,
  td {
    word-wrap: break-word;
    /* older standard */
    overflow-wrap: break-word;
  }

  div.table_container {
    max-height: 35vh;
    overflow: auto;
    margin: auto;
    margin-top: 10px;
    border-radius: 10px;
    width: 100%;

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

  /* Optional: custom scrollbar for WebKit browsers */
  div.table_container::-webkit-scrollbar {
    width: 6px;
  }

  div.table_container::-webkit-scrollbar-track {
    background: transparent;
  }

  div.table_container::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.4);
    border-radius: 20px;
  }


  td:last-child {
    text-align: center;
  }

  .ok {
    color: #097b48;
  }

  .expiring {
    color: #7b6009;
  }

  .expired {
    color: #7b1409;
  }


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

  .homeModal {
    text-align: left;
    border-radius: 15px;
    max-width: 50vw;
    /* Apple Glassmorphism base */
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
  }




  ::placeholder {
    color: white;
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

  img.icon {
    height: 18px;
    vertical-align: middle;
  }

  /* 🔥 This styles the dim background when the dialog is open */
  ::v-deep(dialog::backdrop) {
    background: rgba(0, 0, 0, 0.6);
    /* semi-transparent black */
    backdrop-filter: blur(5px) saturate(180%);

  }

  div.holder {
    text-align: left;
    border-radius: 10px;
    width: -webkit-fill-available;

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
    ;

    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
    padding: 10px;
    margin-top: 10px;
  }



  h2.modalhead {
    display: inline-block;
    vertical-align: middle;
    color: black;
    font-size: 0.8em;
    text-shadow: 0 0 20px rgb(248, 248, 248)
  }
</style>
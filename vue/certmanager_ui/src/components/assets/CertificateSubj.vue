<template>
    <div>
        <h3 style="">Certificate Subject Data</h3>
        <input v-model="this.subjectData.common_name" type="text" id="common_name" name="common_name"
            placeholder="Common Name (example.com) [CN=example.com]">
        <input v-model="this.subjectData.organisation_name" type="text" id="organisation_name" name="organisation_name"
            placeholder="Organisation Name (Example) [O=Example]">
        <input v-model="this.subjectData.organisational_unit_name" type="text" id="organisational_unit_name"
            name="organisational_unit_name" placeholder="Organisation Unit Name (IT_Department) [OU=IT Department]">
        <input v-model="this.subjectData.email" type="text" id="email" name="email"
            placeholder="Email (mrrobot@example.com) [emailAddress=mrrobot@example.com]">
        <input v-model="this.subjectData.locality" type="text" id="locality" name="locality"
            placeholder="Locality (Little Town) [L=Little Town]">
        <input v-model="this.subjectData.state" type="text" id="state" name="state"
            placeholder="State (Greater London) [ST=Greater London]">
        <input v-model="this.subjectData.country" type="text" id="country" name="country"
            placeholder="Country (UK) [C=UK]">


    </div>
</template>

<script>
    export default {
        name: 'CertificateSubj',
        components: {

        },
        data() {
            return {
                subjectData: {
                    "common_name": undefined,
                    "organisation_name": undefined,
                    "organisational_unit_name": undefined,
                    "email": undefined,
                    "locality": undefined,
                    "state": undefined,
                    "country": undefined
                }
            }
        },
        methods: {
            returnPayload: function () {
                let payload = {}

                for (var key in this.subjectData) {
                    console.log(key, this.subjectData[key])
                    if (this.subjectData[key] != undefined && this.subjectData[key] != "") {
                        payload[key] = this.subjectData[key]

                    }
                }
                return payload
            }
        }
    }
</script>

<style scoped>
    input[type="text"],
    input[type="password"] {
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
      color: rgb(248, 247, 247);
    }
</style>
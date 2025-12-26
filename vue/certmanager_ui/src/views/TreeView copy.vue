<template>
    <div style="text-align: left; margin-left:10px;">
        <h1 style="margin-bottom: 0px;">Tree View</h1>
        <p>Note this may take time to load if many certificates are in the store.</p>

        <div style="border-radius: 5px; padding: 5px; overflow: scroll; max-height: 75vh;">
            <div v-for="ca in this.authorities" :key="ca.sys_id">
                <hr>
                <h4 style="margin-bottom: 5px; font-size: 1.1em;">🔒&nbsp;&nbsp;{{ ca.name }}</h4>
                <p style="margin-top: 0px; margin-left: 2.5em; font-family: monospace;"> - Common Name:
                    <b>{{ ca.common_name }}</b>, Created On: <b>
                        {{ unix_to_ts(ca.created) }} </b><br>- Days remaining: <b> {{ ca.remaining_days }} </b>
                    (status::{{ ca.status }})</p>
                <div style="margin-left: 30px;">
                    <p v-if="this.certificates.filter(item => item.parent_ca_sys_id == ca.sys_id).length"
                        style="font-size: 1.2em; font-family: monospace;"> <b>[Parent to
                            {{ this.certificates.filter(item => item.parent_ca_sys_id == ca.sys_id).length }}
                            certificates]</b></p>


                    <div v-show="ca.sys_id == cert.parent_ca_sys_id" v-for="cert in this.certificates" :key="cert.name">

                        <div style="">
                            <h4 style="margin-bottom: 5px; font-size: 1.05em; margin-left: 5px;">{{ cert.name }}</h4>
                            <p style="margin-top: 0px; margin-left:1.2em; font-family: monospace;">- Common Name:
                                <b>{{ cert.common_name }}</b>, Created On: <b>
                                    {{ unix_to_ts(cert.created) }} </b><br> Days remaining <b> {{ cert.remaining_days }}
                                </b>
                                (status::{{ cert.status }})</p>
                                <hr>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>
    <ApiConnect ref="ApiConnect" />
            <NotificationPopup ref="NotificationPopup" />

</template>

<script>
    import ApiConnect from '@/components/ApiConnect.vue'
import NotificationPopup from '@/components/NotificationPopup.vue';

    export default {
        name: 'TreeView',
        components: {
            ApiConnect, NotificationPopup
        },
        data() {
            return {
                authorities: [],
                certificates: [],
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
                    console.log(response)
                    this.authorities = response.result
                    this.authorities_show = response.result
                }

            },

            async get_certificates() {
                var response = await this.$refs.ApiConnect.send_get("/list/certificates/", {}, true)
                if (response != undefined && "result" in response) {
                    this.certificates = response.result
                    this.certificates_show = response.result
                }
            }
        },
        mounted() {
            this.get_authorities()
            this.get_certificates()
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
        font-size: 1.1em;
        border-radius: 5px;
        padding: 10px;
        font-weight: 100;

    }

    button {
        padding: 10px;
        background-color: transparent;
        color: #3a0071;
        border-radius: 5px;
    }

    button:hover {
        background-color: #806e91a1;

    }
</style>
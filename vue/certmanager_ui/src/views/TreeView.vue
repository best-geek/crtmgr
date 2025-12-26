<template>

    <div style="width: 80vw; height: 80vh; margin-left: auto; margin-right: auto; margin-top: 30px;">
        <h2 style="text-align: left;">Relationships</h2>
        <div class="glass_container" style="height: 100%; padding: 10px;">
            <div class="glass_container_divider"
                style="width: 20vw; float: left; text-align: left; height: calc(100% - 15px);">

                <div v-for="ca in this.authorities" :key="ca.sys_id">
                    <button :class="selected_node==ca.sys_id ? 'glass-button-selected': 'glass-button'" style="padding: 10px;"
                        v-on:click="selected_node = ca.sys_id">

                        <h4 style="margin-bottom: 5px; font-size: 1.4em; text-transform:uppercase;">
                            🔒&nbsp;&nbsp;{{ ca.name }}
                        </h4>
                        <p style="margin-top: 0px; margin-left: 5px; font-family: monospace;">

                            Child certificates:
                            {{  this.certificates.filter(item => item.parent_ca_sys_id == ca.sys_id).length }}
                            <br>Common Name:
                            <b>{{ ca.common_name }}</b> <br> Created On: <b>
                                {{ unix_to_ts(ca.created) }} </b><br>Days remaining: <b> {{ ca.remaining_days }} </b>
                            <br>
                            status: {{ ca.status }}</p>

                        <button class="glass-button" style=" text-align: center; width: fit-content; padding: 10px;"
                            @click="$router.push({ path: '/', query: { search: ca.sys_id } })">
                            Details &nbsp;<img class="icon"
          src="/icons/zoom.png">
                        </button>

                    </button>
                    <br>
                </div>

            </div>

            <div class="glass_container_divider"
                style="width: 59vw; float: right; text-align: left; height: calc(100% - 15px)">
                <div>

                    <p style="font-size: 2em; margin-left: 15px;"
                        v-if="certificates == undefined || certificates.length == 0">No certificates found.</p>

                    <div v-show="selected_node == cert.parent_ca_sys_id" v-for="cert in this.certificates"
                        :key="cert.name">

                        <div class="glass_container" style="padding: 10px; margin: 10px; width: calc(58vw - 30px);">
                            <h4 style="margin-bottom: 5px; font-size: 1.05em; margin-left: 5px;">{{ cert.name }}</h4>
                            <p style="margin-top: 0px; margin-left:1.2em; font-family: monospace;">Common Name:
                                <b>{{ cert.common_name }}</b> <br> Created On: <b>
                                    {{ unix_to_ts(cert.created) }} </b><br> Days remaining: <b>
                                    {{ cert.remaining_days }}
                                </b>
                                (status::{{ cert.status }})</p>
                            <button class="glass-button" style=" text-align: center; width: fit-content; padding: 10px;"
                                @click="$router.push({ path: '/', query: { search: `${cert.name}_${cert.parent_ca_sys_id}` } })">
                                Details &nbsp;<img class="icon"
          src="/icons/zoom.png">
                            </button>
                        </div>
                    </div>


                </div>
            </div>
        </div>
    </div>




    <ApiConnect ref="ApiConnect" />

</template>

<script>
    import ApiConnect from '@/components/ApiConnect.vue'
    import emitter from '@/eventBus';

    export default {
        name: 'TreeView',
        components: {
            ApiConnect,
        },
        data() {
            return {
                authorities: [],
                certificates: [],
                selected_node: null
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
            }
        },
        async mounted() {
            await this.get_authorities()
            this.get_certificates()

            if (this.selected_node != null && this.selected_node.length > 0) {
                this.selected_node = this.authorities[0]['sys_id']
            }
        }
    }
</script>

<style scoped>
    h2 {
        margin: 1px;
        text-transform: uppercase;
        font-weight: 400;
    }

    h4{
        margin-top: 5px;
    }

    div.glass_container {
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
        ;

        /* Smooth scroll for nice feel */
        scrollbar-width: thin;
        scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
    }



    div.glass_container_divider {
        overflow: auto;
        margin: auto;
        margin-top: 10px;
        margin-bottom: 10px;
        border-radius: 10px;

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
    }


    .glass-button {
        padding: 15px 25px;
        border-radius: 5px;
        font-size: 0.9em;
        font-weight: 500;
        margin: 5px;
        width: calc(100% - 10px);
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
        font-size: 0.9em;
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
</style>
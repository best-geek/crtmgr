<template>


    <div style="width: 40vw; margin-left: auto; margin-right: auto; margin-top:20px">
        <br>

        <h2 style="text-align: left; margin-left: 0vw;">CREATE {{ certificateType in resolveNiceName ? resolveNiceName[certificateType] : '' }}</h2>

        <div class="outer_container" style="margin-left: auto; margin-right: auto; padding-bottom: 0px;">
            <div class="holder">
                <div style="text-align: center; margin-left: auto; margin-right: auto;">
                    <div v-if="this.certificateType==undefined">
                        <h2>Select Certificate Type</h2>
                        <br>
                        <div>
                            <button style="width: 200px; height: 200px;" class="glass-button"
                                v-on:click="this.certificateType='ca'">
                                <img class="icon" src="/icons/flow_diagram.png">
                                <br><br>
                                <b> Certificate Authority </b>
                                <p style="color: white; font-size: 0.9em;">A certificate that can be used to
                                    establish a
                                    chain
                                    of trust</p>
                            </button>
                            &nbsp;
                            <button style="width: 200px; height: 200px;" class="glass-button"
                                v-on:click="this.certificateType='cert'">
                                <img class="icon" src="/icons/certificate.png">
                                <br><br>
                                <b> Certificate </b>
                                <p style="color: white; font-size: 0.9em;">


                                    A certificate that can be used on a
                                    server
                                    within
                                    the
                                    realm of an authority</p>
                            </button>
                        </div>
                    </div>


                    <div v-if="this.certificateType=='cert'">
                        <CreateCertWindow></CreateCertWindow>
                    </div>

                    <div v-if="this.certificateType=='ca'">
                        <CreateCaWindow></CreateCaWindow>
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import CreateCaWindow from './assets/CreateCaWindow.vue';
    import CreateCertWindow from './assets/CreateCertWindow.vue';


    export default {
        name: 'CreateCert',
        components: {
            CreateCertWindow,
            CreateCaWindow

        },
        data() {
            return {
                certificateType: undefined, 
                resolveNiceName: {
                    "ca": "Certificate Authority",
                    "cert": "Certificate"
                }
            }
        },
        mounted() {
            if (this.$route.query.show) {
                this.certificateType = this.$route.query.show
            }
        }
    }
</script>

<style scoped>
    input[type="text"],
    input[type="password"] {
        font-size: 1.0em;
        border: solid 2px #3a0071;
        border-radius: 5px;
        padding: 10px;
        font-weight: 100;
        min-width: 500px;
        margin-bottom: 5px;

    }

    h3 {
        margin-bottom: 2px;
    }


    .glass-button {
        padding: 9.5px 20px;
        border-radius: 5px;
        font-size: 16px;
        font-weight: 500;
        color: #fff;
        /* White text works best on glass */
        cursor: pointer;
        text-align: center;

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

        /* Smooth transition */
        transition: all 0.3s ease;
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

    div.outer_container {
        max-height: 80vh;
        overflow: auto;
        margin: 10px;
        border-radius: 10px;
        max-width: 80vw;


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
    }

    /* Optional: custom scrollbar for WebKit browsers */
    div.outer_container::-webkit-scrollbar {
        width: 6px;
    }

    div.outer_container::-webkit-scrollbar-track {
        background: transparent;
    }

    div.outer_container::-webkit-scrollbar-thumb {
        background-color: rgba(255, 255, 255, 0.4);
        border-radius: 20px;
    }

    div.holder {
        border-radius: 10px;
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
        margin: 15px;
    }

    h2 {
        margin: 1px;
        text-transform: uppercase;
        font-weight: 400;
        color: white;
    }

    img.icon {
        height: 50px;
        width: 50px;
    }
</style>
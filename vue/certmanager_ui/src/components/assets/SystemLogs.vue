<template>
    <SetSyslog ref="SetSyslog" />

    <div style="margin-left: 15px">

        <h3>System Logs</h3>


        <button @click="toggle_stream(); this.notification('success', `Changed stream mode`)" class="glass-button"
            style="margin-left: 0px; margin-top: 10px;"><img class="icon"
                :src=" this.streamMode ? '/icons/stop.png': '/icons/play.png' ">&nbsp;
            {{ this.streamMode ? 'Stop stream' : 'Streaming mode'  }}</button>



        <button @click="this.autoScroll = !this.autoScroll" class="glass-button"
            style="margin-left: 0px; margin-top: 10px;"><img class="icon"
                :src=" this.autoScroll ? '/icons/stop.png': '/icons/pause.png' ">&nbsp;
            {{ this.streamMode ? 'Stop autoscroll' : 'Autoscroll'  }}</button>


        <button @click="$refs.SetSyslog.showModal()" class="glass-button"
            style="margin-left: 0px; margin-top: 10px;"><img class="icon" src="/icons/chat_room.png">&nbsp;
            Configure Syslog</button>


        <div ref="logContainer" class="holder" style="height: 64vh; margin-right: 10px; overflow: scroll;">
            <pre style="white-space: pre; color: rgb(55, 55, 55);">
                {{ this.logContent }}
            </pre>
        </div>





    </div>
    <ApiConnect ref="ApiConnect" />


</template>

<script>
    import emitter from '@/eventBus';
    import ApiConnect from '../ApiConnect.vue';
    import SetSyslog from './SetSyslog.vue';



    export default {
        name: 'SystemLogs',
        components: {
            ApiConnect,
            SetSyslog
        },
        data() {
            return {

                autoScroll: true,
                streamMode: false,
                logContent: "getting system logs...",
                streamInterval: null

            }
        },
        methods: {

            notification(type, content) {
                emitter.emit('notificationContent', {
                    "type": type,
                    "content": content
                });

            },

            unix_to_ts(unixTimestamp) {
                const date = new Date(unixTimestamp * 1000); // convert to milliseconds
                return date.toLocaleString();
            },



            async get_system_logs_static() {
                var response = await this.$refs.ApiConnect.send_get("/system/logs/", {}, true)
                if (response != undefined && "result" in response && "log" in response['result']) {
                    this.logContent = response['result']['log']
                }
            },


            async toggle_stream() {

                // Toggle stream mode
                this.streamMode = !this.streamMode;

                if (this.streamMode) {
                    // Start interval
                    this.streamInterval = setInterval(() => {
                        this.get_system_logs_stream();
                    }, 2000);
                } else {
                    // Stop interval
                    if (this.streamInterval) {
                        clearInterval(this.streamInterval);
                        this.streamInterval = null;
                    }
                    // Refresh static logs one last time when stopping
                    this.get_system_logs_static();
                }


            },

            async get_system_logs_stream() {
                var response = await this.$refs.ApiConnect.send_get("/system/logs/?stream=true", {}, true)
                if (response != undefined && "result" in response && "log" in response['result']) {
                    this.logContent = response['result']['log']
                }
            },
        },
        mounted() {
            this.get_system_logs_static()
        },
        unmounted() {
                                // Stop interval
                    if (this.streamInterval) {
                        clearInterval(this.streamInterval);
                        this.streamInterval = null;
                    }

        },
        watch: {
            logContent() {
                this.$nextTick(() => {
                    const container = this.$refs.logContainer;
                    if (container && this.autoScroll) {
                        container.scrollTo({
                            top: container.scrollHeight,
                            behavior: 'smooth'
                        });
                    }
                });
            }
        }
    }
</script>

<style scoped>
    input[type="text"],
    input[type="password"] {
        font-size: 1.0em;
        border-radius: 5px;
        border: unset;
        padding: 10px;
        font-weight: 100;
        min-width: 500px;
        margin-bottom: 5px;

    }

    h3 {
        margin-bottom: 2px;
        text-transform: uppercase;
        color: white;
        font-weight: 400;
        font-size: 1.2em;
    }

    p {
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


    img.icon {
        height: 18px;
        vertical-align: middle;
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
</style>
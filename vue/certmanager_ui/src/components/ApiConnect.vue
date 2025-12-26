<template>
    <div>

    </div>
</template>

<script>
    import axios from "axios";
    import emitter from '../eventBus.js';

    export default {
        name: 'ApiConnect',
        components: {
        },
        data() {
            return {
                username: "",
                password: ""
            }
        },
        methods: {
            resolve_api_url() {
                const productionLocation = "/api"
                const devLocation = "http://127.0.0.1:5001"
                if (process.env.NODE_ENV === 'development') {
                    console.log(`${devLocation} selected for API calls`)
                    return devLocation
                } else {
                    return productionLocation
                }

            },

            get_current_bearer() {
                var stored = localStorage.getItem("crtmgr-jwt")
                return stored
            },

            process_err_warning(response) {
                console.log("errors warnings", response)


                if (response == undefined) return

                if ("warnings" in response) {
                    response.warnings.forEach(element => {
                        emitter.emit('notificationContent', {"type":"warning", "content":`API warning: ${element}`});

                    });
                }

                if ("errors" in response) {
                    response.errors.forEach(element => {
                        emitter.emit('notificationContent', {"type":"error", "content":`API error: ${element}`});
                    });
                }

            },

            set_jwt_in_resp(response) {
                if ("token" in response) {
                    localStorage.setItem("crtmgr-jwt", response['token'])
                }

            },
            parse_jwt(token) {
                var base64Url = token.split('.')[1];
                var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
                    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                }).join(''));

                return JSON.parse(jsonPayload);
            },

            get_jwt() {
                var stored = localStorage.getItem("crtmgr-jwt")
                try {
                    var decoded = this.parse_jwt(stored)
                    return decoded
                } catch {
                    return null
                }

            },

            async send_post(uri, payload, head, redirect403 = true) {
                emitter.emit('loadingContent', true);
                const fullUrl = `${this.resolve_api_url()}${uri}`
                var headers = {
                    "Content-Type": "application/json"
                }

                if (this.get_current_bearer() != undefined) {
                    headers['Authorization'] = `Bearer ${this.get_current_bearer()}`
                }

                if (head != undefined) {
                    headers = {
                        ...headers,
                        ...head
                    };
                }

                try {

                    const response = await axios.post(fullUrl, payload, {
                        'headers': headers
                    });
                    this.set_jwt_in_resp(response.data)
                    this.process_err_warning(response.data)
                    emitter.emit('loadingContent', false);

                    return response.data
                } catch (err) {
                    emitter.emit('loadingContent', false);

                    try {
                        this.process_err_warning(err.response.data)
                    } catch {
                        console.log("API error:", err);
                        console.log(err.status)
                    }

                    // do not add a notification if we are on the logon screen already. Most 403's push us here.
                    // removing for now, not bearing much value
                    console.log("API error:", err);
                    if (err.status != 403) {
                        emitter.emit('notificationContent', {"type":"error", "content":`API error calling: ${err}`});
                
                    }

                    if (err.status == 403) {

                        if (redirect403 === true) {
                            this.$router.push("/login")
                        }
                        return err.response.data
                    }
                } finally {
                    // end loading here
                }

            },

            async send_get(uri, head, redirect403 = true, isJson = true) {
                emitter.emit('loadingContent', true);

                const fullUrl = `${this.resolve_api_url()}${uri}`
                var headers = {
                    "Content-Type": "application/json"
                }

                if (this.get_current_bearer() != undefined) {
                    headers['Authorization'] = `Bearer ${this.get_current_bearer()}`
                }

                if (head != undefined) {
                    headers = {
                        ...headers,
                        ...head
                    };
                }

                console.log(isJson)


                try {
                    const response = await axios.get(fullUrl, {
                        headers,
                        responseType: isJson ? 'json' : 'blob'
                    });

                    if (!isJson) return response.data;
                    this.set_jwt_in_resp(response.data)
                    console.log(response.data);
                    this.process_err_warning(response.data)
                    emitter.emit('loadingContent', false);

                    return response.data
                } catch (err) {
                    emitter.emit('loadingContent', false);

                    try {
                        this.process_err_warning(err.response.data)
                    } catch {
                        console.log("API error:", err);
                        console.log(err.status)


                    }


                    // do not add a notification if we are on the logon screen already. Most 403's push us here.
                    console.log("API error:", err);
                    if (err.status != 403) {
                        emitter.emit('notificationContent', {"type":"error", "content":`API error calling: ${err}`});

                        
                    }
                    this.process_err_warning(err)
                    console.log(err.status)
                    if (err.status == 403) {
                        if (redirect403 === true) {
                            this.$router.push("/login")
                        }
                        return err.response.data
                    }
                } finally {
                    // end loading here
                }

            },
            download_authority_buffered: async function (caid) {
                var downloadUrl = `/download/certauthority/${caid}/?buffer=true`
                const result = await this.send_get(downloadUrl, {}, true, false)
                const filename = caid + ".pem"
                console.log(result)


                const blob = new Blob([result], {
                    type: "text/plain"
                });
                const url = URL.createObjectURL(blob);

                const a = document.createElement("a");
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();

                // cleanup
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            },

            download_certificate_buffered: async function (caid, certname) {
                var downloadUrl = `/download/certificate/${caid}/${certname}/?buffer=true`
                const result = await this.send_get(downloadUrl, {}, true, false)

                const filename = `${caid}_${certname}".zip`
                console.log(result)


                const blob = new Blob([result], {
                    type: "text/plain"
                });
                const url = URL.createObjectURL(blob);

                const a = document.createElement("a");
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();

                // cleanup
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            },



        }
    }
</script>

<style scoped>

</style>
<template>

    <div style="width: 80vw; height: 80vh; margin-left: auto; margin-right: auto; margin-top: 30px;">
        <h2 style="text-align: left;">API Documentation</h2>
        <div class="glass_container" style="height: 100%; padding: 10px;">
            <div class="glass_container_divider"
                style="width: 20vw; float: left; text-align: left; height: calc(100% - 15px);">

                
                <div>
                    <button style="vertical-align: middle; padding: 15px"
                        :class="selected_node=='api_overview' ? 'glass-button-selected': 'glass-button'"
                        v-on:click="selected_node = 'api_overview'">


                        <img src="/icons/help.png"
                            style="height: 20px; display: inline-block; vertical-align: middle; margin-top: 0px;">
                        <h4
                            style="margin-bottom: 0px; margin-top: 0px; vertical-align: middle; font-weight: 300; font-size: 1.2em; display: inline-block;">
                            &nbsp; Help </h4>


                    </button>
                    <br>
                </div>
                
                <div v-for="call in this.API_DATA" :key="call.category">
                    <button style="vertical-align: middle; padding: 15px"
                        :class="selected_node==call.category? 'glass-button-selected': 'glass-button'"
                        v-on:click="selected_node = call.category">


                        <img :src="call.icon"
                            style="height: 20px; display: inline-block; vertical-align: middle; margin-top: 0px;">
                        <h4
                            style="margin-bottom: 0px; margin-top: 0px; vertical-align: middle; font-weight: 300; font-size: 1.2em; display: inline-block;">
                            &nbsp; {{ call.category }} </h4>



                    </button>
                    <br>
                </div>

            </div>

            <div class="glass_container_divider"
                style="width: 59vw; float: right; text-align: left; height: calc(100% - 15px)">
                <div>

                    <div class="glass_container" v-show="selected_node=='api_overview'" style="padding: 10px; margin: 10px; width: calc(58vw - 30px);">
                        <p style="font-size: 1.3em; font-weight: 700; margin-top: 4px;">Help</p>
                            <b>- API Endpoint -</b>
                            <p>The API Endpoint is available at <span style="font-family: monospace; font-weight:600"> /api/ </span>of this HTTP server. Ensure that all requests end in a trialing forward slash (/) otherwise you may receive HTTP 404 responses. </p>
                            <br>
                            <b>- Authentication -</b>
                            <p>Use the documentation on this page to determine if your API request requires authentication when being accessed. This is common for most API endpoints. API Keys can be set up by selecting 'Settings' and creating a new API key. <br><br> API authentication should be passed in the <span style="font-family: monospace; font-weight:600"> authorization </span> header of the request. The value of this should be set to <span style="font-family: monospace;font-weight:600">Bearer api_key </span>.</p>
                            <br>
                            <b>- Role Based Access -</b>
                            <p>Certain API calls require a minimum permission to function. This is documented for each API call. When creating your API key, permissions are assigned at creation. It is important to determine what role are required before making a key, as roles cannot be changed after key creation.<br><br> It is best-practice to set the minimum permission. For example, a key that is only needed to manage users should only have the <span style="font-family: monospace; font-weight:600">manage_users</span> permission set.</p>






                        
                    </div>


                    <div v-for="end in (this.API_DATA.find(item => item.category == this.selected_node)?.endpoints || [])"
                        :key="end">

                        <div class="glass_container" style="padding: 10px; margin: 10px; width: calc(58vw - 30px);">
                            <p style="font-size: 1.1em; font-weight: 700; margin-top: 4px;">
                                {{ `/api${end.path}` }}</p>

                            <div style="margin-left: 10px;">


                                <p style="font-family: monospace;"> {{ end['description'] }}</p>


                                <p style="margin-bottom: 0px;"><b>Methods:</b> {{ end.method }}</p>
                                <p style="margin-top: 0px;"><b>Authentication:</b> {{ end.auth }}</p>
                                <p style="font-family: monospace; margin-top: 1px; margin-bottom: 2px;"> <b>Limited to roles:</b>
                                    {{ end['roles'] }}</p>

                                <p style="font-family: monospace; margin-top: 1px; margin-bottom: 2px;"> <b>Required in payload</b>
                                    {{ end['required_json'] }}</p>
                                <p style="font-family: monospace; margin-top: 1px; margin-bottom: 2px;"> <b>Optional fields</b>
                                    {{ end['optional_json'] }}</p>

                            </div>

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

    export default {
        name: 'ApiDocs',
        components: {
            ApiConnect,
        },
        data() {
            return {
                selected_node: null,
                API_DATA: [{
                        category: "Certificate Authorities",
                        icon: '/icons/flow_diagram.png',
                        endpoints: [{
                                path: "/create/certauthority/",
                                method: "POST",
                                auth: "auth_required",
                                roles: ["*", "write"],
                                description: "Creates a new CA, generating a private key and a self-signed certificate. Used as the root for issuing other certificates.",
                                required_json: ["name", "keyphrase"],
                                optional_json: ["ca_days_length", "common_name", "country", "state", "city",
                                    "organization", "email"
                                ],
                            },
                            {
                                path: "/delete/certauthority/<ca_id>/",
                                method: "GET",
                                auth: "auth_required",
                                roles: ["*", "write"],
                                description: "Deletes the specified Certificate Authority.",
                                required_json: [],
                                optional_json: [],
                            },
                            {
                                path: "/list/certauthority/",
                                method: "GET",
                                auth: "auth_required",
                                roles: ["*", "read"],
                                description: "Lists all available Certificate Authorities.",
                                required_json: [],
                                optional_json: [],
                            },
                            {
                                path: "/download/certauthority/<ca_id>/",
                                method: "GET",
                                auth: "auth_required",
                                roles: ["*", "read", "write"],
                                description: "Downloads the CA's .pem file. Use buffer=true for raw binary format instead of JSON.",
                                required_json: [],
                                optional_json: [],
                            },
                        ]
                    },
                    {
                        category: "Certificates",
                        icon: '/icons/certificate.png',
                        endpoints: [{
                                path: "/create/certificate/<ca_id>/",
                                method: "POST",
                                auth: "auth_required",
                                roles: ["*", "write"],
                                description: "Creates a new client/server certificate signed by the specified Certificate Authority.",
                                required_json: ["name", "keyphrase", "ca_name"],
                                optional_json: ["cert_days_length", "common_name", "country", "state", "city",
                                    "organization", "email"
                                ],
                            },
                            {
                                path: "/delete/certificate/<ca_id>/<cert_name>/",
                                method: "GET",
                                auth: "auth_required",
                                roles: ["*", "write"],
                                description: "Deletes a specific certificate by name. Must specify the parent authority ID.",
                                required_json: [],
                                optional_json: [],
                            },
                            {
                                path: "/list/certificates/",
                                method: "GET",
                                auth: "auth_required",
                                roles: ["*", "read"],
                                description: "Lists all individual certificates.",
                                required_json: [],
                                optional_json: [],
                            },
                            {
                                path: "/download/certificate/<ca_id>/<cert_name>/",
                                method: "GET",
                                auth: "auth_required",
                                roles: ["*", "read", "write"],
                                description: "Downloads the .crt and .key files. Use buffer=true for .zip binary file",
                                required_json: [],
                                optional_json: [],
                            },
                        ]
                    },
                    {
                        category: "User and Authentication",
                        icon: '/icons/user.png',
                        endpoints: [{
                                path: "/user/login/",
                                method: "POST",
                                auth: "None (Unauthenticated)",
                                description: "Authenticates a user using credentials. Returns a token in response which should be used for further requests.",
                                required_json: ["username", "password"],
                                optional_json: [],
                            },
                            {
                                path: "/user/resetpassword/<for_user>/",
                                method: "POST",
                                auth: "auth_required",
                                roles: ["*", "manage_users"],
                                description: "Allows a user to change their password. 'password' value is for the actors password.",
                                required_json: ["password", "new_password"],
                                optional_json: [],
                            },
                            {
                                path: "/user/details/me/",
                                method: "GET",
                                auth: "auth_required",
                                roles: [],
                                description: "Get details for the authenticated user token.",
                                required_json: [],
                                optional_json: [],
                            },
                            {
                                path: "/user/details/list/",
                                method: "GET",
                                auth: "auth_required",
                                roles: ["*", "manage_users"],
                                description: "Lists all users.",
                                required_json: [],
                                optional_json: [],
                            },
                            {
                                path: "/user/create/",
                                method: "POST",
                                auth: "auth_required + Role: * or manage_users",
                                roles: ["*", "manage_users"],
                                description: "Creates a new user account. Password is generated in response.",
                                required_json: ["username", "roles"],
                                optional_json: [""],
                            },
                            {
                                path: "/user/profile/<for_user>/update/",
                                method: "POST",
                                auth: "auth_required + Role: * or manage_users",
                                roles: ["*", "manage_users"],
                                description: "Updates user roles or other profile elements. Note role assignment scope is limited to that of the authenticated user.",
                                required_json: [],
                                optional_json: ["roles"],
                            },
                            {
                                path: "/user/profile/<for_user>/delete/",
                                method: "POST",
                                auth: "auth_required + Role: * or manage_users",
                                roles: ["*", "manage_users"],
                                description: "Deletes a user account. Cannot delete self.",
                                required_json: [],
                                optional_json: [],
                            },
                        ]
                    },
                    {
                        category: "API Keys",
                        icon: '/icons/our_process.png',
                        endpoints: [{
                                path: "/user/apikeys/create/",
                                method: "POST",
                                auth: "auth_required",
                                roles:[],
                                description: "Generates a new API key for API access, which can have specific roles and expiry. Note role assignment scope is limited to that of the authenticated user.",
                                required_json: ["roles", "days_expiry"],
                                optional_json: [],
                            },
                            {
                                path: "/user/apikeys/list/",
                                method: "GET",
                                auth: "auth_required",
                                roles:[],
                                description: "Lists API keys belonging to the current user.",
                                required_json: [],
                                optional_json: [],
                            },
                            {
                                path: "/user/apikeys/delete/<keyid>/",
                                method: "GET",
                                auth: "auth_required",
                                roles:[],
                                description: "Deletes a specific API key. Only the owner can delete keys",
                                required_json: [],
                                optional_json: [],
                            },
                        ]
                    },
                    {
                        category: "System",
                        icon: '/icons/system.png',
                        endpoints: [{
                                path: "/system/logs/",
                                method: "GET",
                                auth: "auth_required",
                                description: "Retrieves 'audit.log' content.",
                                roles:[],
                                required_json: [],
                                optional_json: ["URL param: stream=true for live feed"],
                            },
                            {
                                path: "/system/logs/syslog/",
                                method: "POST",
                                auth: "auth_required",
                                roles:["*","system_admin"],
                                description: "Configures remote syslog forwarding. **Triggers API restart.**",
                                required_json: ["host", "port"],
                                optional_json: [],
                            },
                            {
                                path: "/",
                                method: "GET/POST",
                                auth: "None (Unauthenticated)",
                                roles:[],
                                description: "Health check endpoint (ping/pong).",
                                required_json: [],
                                optional_json: [],
                            },
                        ]
                    },
                ]
            }
        },
        methods: {
            unix_to_ts(unixTimestamp) {
                const date = new Date(unixTimestamp * 1000); // convert to milliseconds
                return date.toLocaleString();
            },

        },
        async mounted() {
            this.selected_node = 'api_overview'
        }
    }
</script>

<style scoped>
    div.glass_container {
    overflow: auto;
    margin: auto;
    margin-top: 10px;
    border-radius: 10px;
    width: 100%;

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

  background: linear-gradient(
    to bottom right,
    rgba(50, 50, 50, 0.35),
    rgba(30, 30, 30, 0.15)
  );
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

    h2 {
        margin: 1px;
        text-transform: uppercase;
        font-weight: 400;
    }
</style>
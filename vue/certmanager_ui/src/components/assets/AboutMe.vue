<template>
    <div style="margin-left: 15px">
        <PasswordModal ref="PasswordModal" />
        <ApiKeyCreate ref="ApiKeyCreate" />



        <br>


        <div style="height: 70px; display: inline-block; vertical-align: top;">
            <img style="height: 100%;" src="/icons/user.png">&nbsp;
        </div>

        <div style="display: inline-block;">
            <h3>{{ this.UserProfile.username || "Not populated" }}</h3>
            <p style="margin-top:3px"><b>Active Since:</b> {{ unix_to_ts(this.UserProfile.created) }}</p>
            <button @click="$refs.PasswordModal.showModal()" class="glass-button" style="margin-left: 0px;"><img
                    class="icon" src="/icons/password.png">&nbsp;Change User
                Password</button>
        </div>




        <p style="margin-bottom: 5px;"><b>Roles:</b></p>



        <table cellpadding="8" cellspacing="0" class="table_container" style="margin-bottom: 10px;">
            <thead>
                <tr>
                    <th>Role</th>
                    <th>Permission</th>
                </tr>
            </thead>
            <tbody>

                <tr v-for="roles in JSON.parse(this.UserProfile.roles)" :key="roles">
                    <td style="font-weight: 500;">{{roles }}</td>
                    <td><i style="color: bisque;">{{ RoleDescription[roles] }}</i></td>
                </tr>

            </tbody>
        </table>


        <br><br>
        <h3 style="display: inline-block;">API Keys ({{ ApiKeys.length }})</h3> <button
            style="display: inline-block; margin: 5px; padding: 5px;" class="glass-button"
            @click="$refs.ApiKeyCreate.showModal()">Create Key</button>

        <table id="apikeystbl" cellpadding="8" cellspacing="0" class="table_container" style="margin-bottom: 10px;">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Created</th>
                    <th>Expires</th>
                    <th>Roles</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>

                <tr v-for="ky in this.ApiKeys" :key="ky.username">
                    <td style="font-weight: 500;">{{ ky.username }}</td>
                    <td>{{ unix_to_ts(ky.created) }}</td>
                    <td>{{ unix_to_ts(ky.expires)}}</td>
                    <td>
                        <p v-for="roles in JSON.parse(ky.roles)" :key="roles"
                            style="margin-top: 3px;margin-left: 15px; color: bisque;">
                            {{` ${roles}` }} <i>{{ RoleDescription[roles] }}</i></p>
                    </td>
                    <td>
                        <button class="glass-button" @click="delete_apikeys(ky.username)"
                            style="margin-right: 5px; padding: 5px;">🗑️</button>
                    </td>
                </tr>

            </tbody>
        </table>
    </div>
    <ApiConnect ref="ApiConnect" />


</template>

<script>
    import emitter from '@/eventBus';
    import ApiConnect from '../ApiConnect.vue';
    import ApiKeyCreate from './ApiKeyCreate.vue';
    import PasswordModal from './PasswordModal.vue';


    export default {
        name: 'AboutMe',
        components: {
            ApiConnect,
            PasswordModal,
            ApiKeyCreate
        },
        data() {
            return {

                UserProfile: {
                    "username": "sample_user",
                    "created": 12345678,
                    "roles": "[\"*\"]"
                },

                RoleDescription: {
                    "*": "All functionality (inherits everything)",
                    "read": "Read all certificate data",
                    "write": "Write all certificate data",
                    "manage_users": "Create, delete and change password for a user"
                },

                ApiKeys: []

            }
        },
        methods: {
            showPassword() {
                this.$refs.PasswordModal.showModal()
            },

            unix_to_ts(unixTimestamp) {
                const date = new Date(unixTimestamp * 1000); // convert to milliseconds
                return date.toLocaleString();
            },

            returnPayload: function () {
                let payload = {}

                for (var key in this.subjectData) {
                    console.log(key, this.subjectData[key])
                    if (this.subjectData[key] != undefined && this.subjectData[key] != "") {
                        payload[key] = this.subjectData[key]

                    }
                }
                return payload
            },

            async get_apikeys() {
                var response = await this.$refs.ApiConnect.send_get("/user/apikeys/list/", {}, true)
                if (response != undefined && "result" in response && "keys" in response['result']) {
                    this.ApiKeys = response['result']['keys']
                }
            },

            async get_user_details_me() {
                var response = await this.$refs.ApiConnect.send_get("/user/details/me/", {}, true)
                if (response != undefined && "result" in response && "users" in response['result']) {
                    this.UserProfile = response['result']['users'][0]
                }
            },

            async delete_apikeys(keyid) {
                var response = await this.$refs.ApiConnect.send_get(`/user/apikeys/delete/${keyid}/`, {}, true)
                if (response != undefined && "result" in response && response['result'] == true) {
                    emitter.emit('notificationContent', {"type":"success","content": `Deleted API key: ${keyid}`});

                    this.get_apikeys()
                }
            }
        },
        mounted() {
            this.get_apikeys()
            this.get_user_details_me()
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


    table {
        margin-top: 10px;
        max-height: 5vh;
        width: 98%;
        border-collapse: separate;
        white-space: wrap;
        table-layout: fixed;
        color: rgb(55, 55, 55);
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
        border-radius: 10px;
        font-size: 0.8em;

    }

    th {
        position: sticky;
        top: 0;
        background: #66656539;
        backdrop-filter: blur(12px) saturate(180%);

        z-index: 1;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin: 10px;
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

    #apikeystbl th:last-child,
    #apikeystbl td:last-child {
        width: 50px;
        /* or whatever you need */
        max-width: 50px;
        /* optional, keeps buttons wrapped */
        text-align: center;
    }

    img.icon {
        height: 18px;
        vertical-align: middle;
    }
</style>
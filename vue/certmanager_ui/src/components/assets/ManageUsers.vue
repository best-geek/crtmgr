<template>
    <div style="margin-left: 15px">
        <PasswordModal ref="PasswordModal" />
        <UserCreate ref="UserCreate"></UserCreate>



        <h3>Manager Users</h3>
        <br>

        <button @click="$refs.UserCreate.showModal()" class="glass-button" style="margin-left: 0px;"><img class="icon"
                src="/icons/add.png">&nbsp;Create New User</button>

        <button @click="get_user_details(); notification({'type':'success', 'content':'Refreshed users'})"
            class="glass-button" style="margin-left: 0px;"><img class="icon" src="/icons/refresh.png">&nbsp;Refresh
            Users</button>


        <table cellpadding="8" cellspacing="0" class="table_container" style="margin-bottom: 10px;">
            <thead>
                <tr>
                    <th style="width: 150px;">Username</th>
                    <th style="width: 150px;">Created</th>
                    <th style="margin-right: auto;">Permissions</th>
                    <th style="text-align: right;">Action</th>
                </tr>
            </thead>
            <tbody>


                <tr v-for="user in allProfiles" :key="user.username">
                    <td style="font-weight: 500;">{{user.username }}</td>
                    <td><i>{{ this.unix_to_ts(user.created)}}</i></td>

                    <td>
                        <DropDownCheckbox style="text-align: left;" :options="this.permissionsOpts"
                            :already_selected="JSON.parse(user.roles)" placeholder="Selected roles"
                            @updateFilter="(roles) => update_roles(roles, user.username)">
                        </DropDownCheckbox>
                    </td>
                    <td style="text-align: right;">
                        <button class="glass-button" @click="$refs.DeleteUser.showModal(user.username)"
                            style="margin-right: 5px; padding: 5px;"><img class="icon" src="/icons/delete.png"></button>

                        <button class="glass-button" @click="$refs.PasswordModal.showModal(user.username)"
                            style="margin-right: 5px; padding: 5px;"><img class="icon" src="/icons/lock.png"></button>
                    </td>
                </tr>


            </tbody>
        </table>


        <br><br>

    </div>
    <ApiConnect ref="ApiConnect" />
    <DeleteUser ref="DeleteUser" />


</template>

<script>
    import ApiConnect from '../ApiConnect.vue';
    import DeleteUser from './DeleteUser.vue';
    import DropDownCheckbox from './DropDownCheckbox.vue';
    import PasswordModal from './PasswordModal.vue';
    import UserCreate from './UserCreate.vue';
    import emitter from '@/eventBus';


    export default {
        name: 'ManageUsers',
        components: {
            ApiConnect,
            PasswordModal,
            UserCreate,
            DropDownCheckbox,
            DeleteUser
        },
        data() {
            return {

                RoleDescription: {
                    "*": "All functionality (inherits everything)",
                    "read": "Read all certificate data",
                    "write": "Write all certificate data",
                    "manage_users": "Create, delete and change password for a user"
                },
                allProfiles: [],
                permissionsOpts: [{
                        "displayName": "Inherit all permissions",
                        "emitValue": "*"
                    },
                    {
                        "displayName": "Read all certificate data",
                        "emitValue": "read"
                    },
                    {
                        "displayName": "Write certificate data",
                        "emitValue": "write"
                    },
                    {
                        "displayName": "Manage user information",
                        "emitValue": "manage_users"
                    },
                ]

            }
        },
        methods: {
            notification(payload) {
                emitter.emit("notificationContent", payload)

            },      

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


            async get_user_details() {
                var response = await this.$refs.ApiConnect.send_get("/user/details/list/", {}, true)
                if (response != undefined && "result" in response && "users" in response['result']) {
                    this.allProfiles = response['result']['users']
                }
                console.log(this.allProfiles)
            },

            update_roles: async function (roles, foruser) {
                console.log("selected:", roles)

                const payload = {
                    "roles": roles,
                }


                var response = await this.$refs.ApiConnect.send_post(`/user/profile/${foruser}/update/`,
                    payload, {},
                    false)

                console.log("typeof response:", typeof response)


                if (response && response.errors && response.errors.length == 0) {
                    this.notification({"type":"success", "content":`Updated role for ${foruser}`})
                }

                // update page
                this.get_user_details()

            }


        },
        mounted() {
            this.get_user_details()
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


    table {
        margin-top: 10px;
        max-height: 5vh;
        width: 98%;
        border-collapse: separate;
        white-space: wrap;
        table-layout: fixed;
        color: rgb(55, 55, 55);
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

    #apikeystbl th:first-of-type,
    #apikeystbl td:first-of-type {
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
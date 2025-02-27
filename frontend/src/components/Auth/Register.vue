<template>
  <div class="container mt-5">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <div class="mb-3">
        <label for="name" class="form-label">Name</label>
        <input type="text" class="form-control" id="name" v-model="name" required />
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" class="form-control" id="email" v-model="email" required />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" v-model="password" required />
      </div>
      <div class="mb-3">
        <label for="invite" class="form-label">Invite Code</label>
        <input type="text" class="form-control" id="invite" v-model="invite" required />
      </div>
      <button type="submit" class="btn btn-primary">Register</button>
    </form>
  </div>
</template>

<script>
import { register } from '../../api/auth';

export default {
  data() {
    return {
      name: '',
      email: '',
      password: '',
      invite: '',
    };
  },
  methods: {
    async handleRegister() {
      try {
        const result = await register({
          name: this.name,
          email: this.email,
          password: this.password,
          invite: this.invite,
        });
        console.log('Registration success:', result);
        this.$router.push('/login');
      } catch (error) {
        alert('Registration failed');
      }
    },
  },
};
</script>
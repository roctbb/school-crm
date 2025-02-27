<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Vue App</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'Login' }">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'Register' }">Register</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'Objects' }">Objects</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <div class="container mt-4">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style>
/* Basic application-wide styles */
body {
  font-family: "Arial", sans-serif;
  margin: 0;
}
</style>
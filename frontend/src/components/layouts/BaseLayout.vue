<template>
    <div class="layout">
        <Navbar/>

        <main class="container page-container">
            <slot/>
        </main>
    </div>
</template>

<script>
import Navbar from "@/components/common/Navbar.vue";

export default {
    name: "BaseLayout",
    components: {
        Navbar,
    },
};
</script>

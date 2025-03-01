<template>
    <div class="layout">
        <!-- Навбар (Общий для всех страниц) -->
        <Navbar/>

        <div class="container py-2">
            <slot/>
        </div>
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

<style scoped>

</style>
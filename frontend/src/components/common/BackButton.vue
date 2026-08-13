<template>
    <button
        class="btn btn-sm btn-light"
        type="button"
        @click="$router.go(-1)"
    >
        <i class="bi bi-arrow-left"></i> Назад
    </button>
</template>

<script>
export default {
    name: "BackButton"
};
</script>

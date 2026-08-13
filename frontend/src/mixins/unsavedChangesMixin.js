export default {
    mounted() {
        window.addEventListener('beforeunload', this.handleUnsavedBeforeUnload);
    },
    beforeUnmount() {
        window.removeEventListener('beforeunload', this.handleUnsavedBeforeUnload);
    },
    beforeRouteLeave(to, from, next) {
        if (!this.hasUnsavedChanges || window.confirm('Есть несохранённые изменения. Покинуть страницу?')) {
            next();
            return;
        }
        next(false);
    },
    methods: {
        handleUnsavedBeforeUnload(event) {
            if (!this.hasUnsavedChanges) return;
            event.preventDefault();
            event.returnValue = '';
        },
    },
};

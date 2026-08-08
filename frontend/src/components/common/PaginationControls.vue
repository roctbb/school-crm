<template>
    <div v-if="totalItems" class="d-flex flex-column flex-sm-row align-items-center justify-content-between gap-2 mt-3">
        <small class="text-muted">
            Показано {{ firstItem }}–{{ lastItem }} из {{ totalItems }}
        </small>

        <nav v-if="totalPages > 1" aria-label="Постраничная навигация">
            <ul class="pagination pagination-sm mb-0">
                <li class="page-item" :class="{disabled: currentPage === 1}">
                    <button
                        class="page-link"
                        type="button"
                        :disabled="currentPage === 1"
                        aria-label="Предыдущая страница"
                        @click="$emit('page-selected', currentPage - 1)"
                    >
                        <span aria-hidden="true">‹</span>
                    </button>
                </li>

                <li
                    v-for="pageNumber in visiblePages"
                    :key="pageNumber"
                    class="page-item"
                    :class="{active: pageNumber === currentPage}"
                >
                    <button
                        class="page-link"
                        type="button"
                        :aria-current="pageNumber === currentPage ? 'page' : undefined"
                        @click="$emit('page-selected', pageNumber)"
                    >
                        {{ pageNumber }}
                    </button>
                </li>

                <li class="page-item" :class="{disabled: currentPage === totalPages}">
                    <button
                        class="page-link"
                        type="button"
                        :disabled="currentPage === totalPages"
                        aria-label="Следующая страница"
                        @click="$emit('page-selected', currentPage + 1)"
                    >
                        <span aria-hidden="true">›</span>
                    </button>
                </li>
            </ul>
        </nav>
    </div>
</template>

<script>
export default {
    name: "PaginationControls",
    emits: ["page-selected"],
    props: {
        currentPage: {type: Number, required: true},
        pageSize: {type: Number, required: true},
        totalItems: {type: Number, required: true},
    },
    computed: {
        totalPages() {
            return Math.max(1, Math.ceil(this.totalItems / this.pageSize));
        },
        firstItem() {
            return (this.currentPage - 1) * this.pageSize + 1;
        },
        lastItem() {
            return Math.min(this.currentPage * this.pageSize, this.totalItems);
        },
        visiblePages() {
            const start = Math.max(1, Math.min(this.currentPage - 2, this.totalPages - 4));
            const end = Math.min(this.totalPages, start + 4);
            return Array.from({length: end - start + 1}, (_, index) => start + index);
        },
    },
};
</script>

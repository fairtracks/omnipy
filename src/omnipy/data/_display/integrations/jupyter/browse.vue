<template>
  <div>
  </div>
</template>

<script>
module.exports = {
  name: 'BrowseModels',
  mounted() {
    this.openAllModels();
  },
  methods: {
    openAllModels() {
      Object.entries(this.html_content).forEach(([key, value]) => {


        // alert(`Opening model: ${key}`);

        const blob = new Blob([value], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        window.open(url, key );

        // Clean up the blob URL after a delay to allow the browser to load it
        setTimeout(() => {
          URL.revokeObjectURL(url);
        }, 1000);
      });
    }
  }}
</script>

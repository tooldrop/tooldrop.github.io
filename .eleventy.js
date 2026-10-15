module.exports = function(eleventyConfig) {
  // Copy static assets
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");
  eleventyConfig.addPassthroughCopy("src/images");
  eleventyConfig.addPassthroughCopy("src/robots.txt");
  eleventyConfig.addPassthroughCopy("src/.nojekyll");
  
  // Add date filter
  eleventyConfig.addFilter("dateDisplay", (dateObj) => {
    if (!dateObj) return "";
    const date = new Date(dateObj);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  });

  // Add slug filter for tool IDs
  eleventyConfig.addFilter("slugify", (str) => {
    return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  });

  // Add filter to get unique categories
  eleventyConfig.addFilter("getCategories", (tools) => {
    const categories = new Set();
    tools.forEach(tool => {
      if (tool.categories) {
        tool.categories.forEach(cat => categories.add(cat));
      }
    });
    return Array.from(categories).sort();
  });

  // Add filter to get tools by category
  eleventyConfig.addFilter("filterByCategory", (tools, category) => {
    return tools.filter(tool => tool.categories && tool.categories.includes(category));
  });

  // Add filter to get new releases (tools with newRelease flag or added in last 30 days)
  eleventyConfig.addFilter("getNewReleases", (tools) => {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    return tools.filter(tool => {
      if (tool.newRelease) return true;
      if (tool.dateAdded) {
        return new Date(tool.dateAdded) >= thirtyDaysAgo;
      }
      return false;
    }).sort((a, b) => new Date(b.dateAdded) - new Date(a.dateAdded));
  });

  // Add filter to get featured tools
  eleventyConfig.addFilter("getFeatured", (tools) => {
    return tools.filter(tool => tool.featured);
  });

  // Add filter to limit array
  eleventyConfig.addFilter("limit", (arr, limit) => {
    return arr.slice(0, limit);
  });

  // Create collection for category pages
  eleventyConfig.addCollection("categories", function(collectionApi) {
    const tools = require('./src/_data/tools.json');
    const categories = new Set();
    tools.forEach(tool => {
      if (tool.categories) {
        tool.categories.forEach(cat => categories.add(cat));
      }
    });
    return Array.from(categories).sort().map(cat => ({
      name: cat,
      slug: cat.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''),
      tools: tools.filter(t => t.categories && t.categories.includes(cat))
    }));
  });

  // Create collection for tool pages
  eleventyConfig.addCollection("toolPages", function(collectionApi) {
    const tools = require('./src/_data/tools.json');
    return tools.map(tool => ({
      ...tool,
      slug: tool.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
    }));
  });

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data"
    },
    templateFormats: ["njk", "md", "html"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};

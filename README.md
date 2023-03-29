# Digital Content Platform (DCP)

DCP is a platform for digital content products. It includes shared libraries and micro-apps for rapid authoring and publishing of content with workflows for technical and non-technical writers.

This monorepo uses the [Nx](https://nx.dev) tool-stack with the [@nxtensions/astro](https://github.com/nxtensions/nxtensions) extension for [Astro](https://astro.build/) support.


## Getting started
The @nxtensions/astro extension generates projects that use targets matching the Astro CLI.

For example, use the following command to to run a project in a development server:
```
npx nx dev dcp-guide
```

This aligns to the `dev` Astro CLI command instead of the nx convention `serve` target. Similarly the `check` target is included, instead of the `lint` target, for static checks.

### Generating micro-apps
@nxtensions/astro extension includes generators for applications and libraries.

Run the nx `list` command to see what is available:
```
npx nx list @nxtensions/astro
```

Run the `application` generator to create a new micro-app:
```
npx nx g @nxtensions/astro:application
```

## Deployment

OpenShift manifests and deployments are maintained in source control and the pipeline automatically applies them during deployment stages. This is convention based and new applications can follow the existing files to adhere to conventions.

Application specific manifests and supporting files are maintained under `.openshift/<sub_project_name>` with a main template in `<sub_project_name>.yml`.

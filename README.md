﻿# Galaxy Social

<div align="center">
      👇</br>
      <kbd><a href="../../new/main/?filename=posts/2025/<your-path>.md&value=---%0Amedia:%0A-%20mastodon%0A-%20bluesky-vgp%0A-%20matrix%0A-%20slack%0A-%20linkedin%0A-%20bluesky%0Amentions:%0A%20%20mastodon:%20[]%0A%20%20bluesky-vgp:%20[]%0A%20%20matrix:%20[]%0A%20%20slack:%20[]%0A%20%20linkedin:%20[]%0A%20%20bluesky:%20[]%0Ahashtags:%0A%20%20mastodon:%0A%20%20-%20UseGalaxy%0A%20%20-%20GalaxyProject%0A%20%20-%20UniFreiburg%0A%20%20-%20EOSC%0A%20%20-%20EuroScienceGateway%0A%20%20bluesky-vgp:%0A%20%20-%20UseGalaxy%0A%20%20-%20GalaxyProject%0A%20%20-%20UniFreiburg%0A%20%20-%20EOSC%0A%20%20-%20EuroScienceGateway%0A%20%20matrix:%0A%20%20-%20UseGalaxy%0A%20%20-%20GalaxyProject%0A%20%20-%20UniFreiburg%0A%20%20-%20EOSC%0A%20%20-%20EuroScienceGateway%0A%20%20slack:%0A%20%20-%20UseGalaxy%0A%20%20-%20GalaxyProject%0A%20%20-%20UniFreiburg%0A%20%20-%20EOSC%0A%20%20-%20EuroScienceGateway%0A%20%20linkedin:%0A%20%20-%20UseGalaxy%0A%20%20-%20GalaxyProject%0A%20%20-%20UniFreiburg%0A%20%20-%20EOSC%0A%20%20-%20EuroScienceGateway%0A%20%20bluesky:%0A%20%20-%20UseGalaxy%0A%20%20-%20GalaxyProject%0A%20%20-%20UniFreiburg%0A%20%20-%20EOSC%0A%20%20-%20EuroScienceGateway%0A%0A---%0AYour%20text%20content%20goes%20here.%20(Markdown%20syntax%20will%20not%20pass%20to%20Bluesky,%20Mastodon,%20and%20Linkedin!)%0AFor%20images%20just%20drag%20and%20drop%20them%20here.%20they%20will%20look%20like%20this:%0A![A](https://example.com/a.jpg)">Create new post</a></kbd>
</div>

## How to Create a Post

To create a post on Galaxy Social, follow these steps:

1. **Create a Branch:** Begin by [creating a branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-and-deleting-branches-within-your-repository#creating-a-branch) in this repository or [your forked repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo#forking-a-repository).

2. **Add a New File:** Within the "posts" folder (or sub-folders), create a new file with the extension ".md" and [commit it to your branch](https://docs.github.com/en/repositories/working-with-files/managing-files/creating-new-files).

3. **Use the Post Template:** Utilize the following template for the post content:

```yaml
---
media:
- mastodon
- bluesky-vgp
- matrix
- slack
- linkedin
- bluesky
mentions:
  mastodon: []
  bluesky-vgp: []
  matrix: []
  slack: []
  linkedin: []
  bluesky: []
hashtags:
  mastodon:
  - UseGalaxy
  - GalaxyProject
  - UniFreiburg
  - EOSC
  - EuroScienceGateway
  bluesky-vgp:
  - UseGalaxy
  - GalaxyProject
  - UniFreiburg
  - EOSC
  - EuroScienceGateway
  matrix:
  - UseGalaxy
  - GalaxyProject
  - UniFreiburg
  - EOSC
  - EuroScienceGateway
  slack:
  - UseGalaxy
  - GalaxyProject
  - UniFreiburg
  - EOSC
  - EuroScienceGateway
  linkedin:
  - UseGalaxy
  - GalaxyProject
  - UniFreiburg
  - EOSC
  - EuroScienceGateway
  bluesky:
  - UseGalaxy
  - GalaxyProject
  - UniFreiburg
  - EOSC
  - EuroScienceGateway

---
Your text content goes here. (Markdown syntax will not pass to Bluesky, Mastodon, and Linkedin!)
For images just drag and drop them here. they will look like this:
![A](https://example.com/a.jpg)
```

**Notes on the Template:**

- Everything between the two `---` are metatags and should be in YAML format.

- "media" (Required): Ensure the media name is implemented inside the `plugins.yml`.

- "mentions" and "hashtags" (Optional): Follow the specified format as shown in the template.

- "Your text content goes here." (Required): This is the content that will be posted to social media platforms.

  Note that some social media platforms do not support Markdown formatting, so use plain text only.

  Dividing long content into multiple threaded posts: when the character limit is reached on a social media, it will be divided into several posts as a thread. You can also define custom breakpoints for splitting the post by inserting 2 empty lines anywhere in the text. The second empty line will simply be removed for media that don't support content splitting.

- "images" (Optional): You can include images using Markdown format at the end of the file like this: `![Alternative text](Link to the image)`. Alternatively, you can simply drag and drop an image from your PC while adding your file.

4. **Create a Pull Request:** Once your post is ready, [create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request?tool=webui#creating-the-pull-request) to the main branch from another branch or [from your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)

5. **Preview and Review:** After each pull request, the GitHub action will run and will generate previews of the content as it would appear on each platform listed under "media" in a comment to the pull request and highlight any errors that need to be fixed before merging.

6. **Publish Your Content:** Upon merging the pull request, the GitHub action will run. The results will be added to `processed_files.json` in the processed_files branch.

By following these steps, you can effectively create and publish posts on Galaxy Social.

## Add a New Social Media Platform

Expanding the capabilities of Galaxy Social by adding a new social media platform is a straightforward process. Follow these steps to integrate a new platform:

1. **Create a Plugin File**: Begin by adding a Python file to the `lib/plugins` folder. This file should contain a class with a function named `create_post(content, mentions, hashtags, images, alt_texts)`. This function will handle the process of sending announcements to the desired social media platform.

2. **Update plugins.yml**: Next, update the `plugins.yml` file to include the new social media platform. Follow this template:

```yaml
- name: name_of_the_media
  class: file_name.class_name
  enabled: true
  config:
    token: $TOKEN_SAVED_IN_PUBLISH_CONTENT
    room_id: "room_id"
```

Ensure to replace `name_of_the_media` with the name of the new platform, and `file_name.class_name` with the appropriate file and class name for the plugin.
The `name` is then used in the `media` tag in the post file (posts/\*.md) to determine the social media.

3. **Configuration**: In the `config` section, specify any required variables for initializing the plugin class. This may include authentication tokens, room IDs, or other platform-specific parameters. Any configuration that needs to be securely passed with GitHub secrets should be prefixed with `$` in order to be easily identifiable within the workflow YAML file.

4. **GitHub Secrets**: Add any tokens or variables required for the plugin to GitHub secrets. This ensures sensitive information is securely stored. Refer to [GitHub secrets documentation](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) for guidance on creating secrets.

5. **Enable the Plugin**: Simply set `enabled: true` to enable the new social media platform. This ensures that it will be implemented when creating posts.

6. **Update galaxy_social.yml**: Finally, update the `galaxy_social.yml` file to include an environment variable referencing the token saved in GitHub secrets. Use the following template: (Don't put the prefixed `$` in here)

```yaml

---
env:
  TOKEN_SAVED_IN_PUBLISH_CONTENT: ${{ secrets.TOKEN_SAVED_IN_GITHUB_SECRETS }}
```

Replace `TOKEN_SAVED_IN_GITHUB_SECRETS` with the name of the secret containing the token for the new social media platform.

By following these steps, you can seamlessly integrate a new social media platform into Galaxy Social, expanding its reach and functionality.

### Duplicate a Social Media Platform with Different Token

If you need to use the same social media platform with different authentication tokens, you can duplicate the entry in the `plugins.yml` file. Follow these steps:

1. **Duplicate Entry**: Copy the entry for the social media platform in the `plugins.yml` file and paste it below the original entry.

2. **Update Name and Tokens**: Change the name of the duplicated entry to reflect the new configuration, and replace the token with the new authentication token.

3. **Configuration**: Adjust any other configuration parameters as needed for the duplicated entry.

4. **Use Name in Post**: Remember that the name you specify in the `plugins.yml` file must also be used within the `media` tag when creating a post. Ensure consistency to link the post with the correct social media platform.

By following these steps, you can effectively duplicate a social media platform with a different token for specific use cases or configurations.

## Run locally

You can execute this repository on your machine by running `lib/galaxy_social.py` with the argument `--files Files ...` or `--folder FOLDER` to process files, or add `--preview` to preview the file as markdown. Also there is `--json-out processed_files.json` that could be change where to save the json results output.

Remember to add the env variable that needed for each social media seperatly.

## Social media implemented

- Bluesky
- Mastodon
- Matrix: hashtags are included in the post but have no special function in matrix.
- Slack: mentions and hashtags are not working!
- Linkedin: mentions are not working!

# Publishing the GitHub portfolio (optional account-level steps)

The portfolio source, case studies and tests live in public repositories. Two presentation features require GitHub account/repository administration actions that the available GitHub connector cannot perform.

## A. Make the profile README appear on the GitHub account overview

1. Under the GitHub account **`reddydev-ai`**, create a **public repository with the exact name `reddydev-ai`**. A README may be initialized at creation.
2. Copy the clean content of [GITHUB_PROFILE_README_READY.md](GITHUB_PROFILE_README_READY.md) to `README.md` **at the root** of that new repository.
3. Check [the GitHub account profile](https://github.com/reddydev-ai) in a signed-out browser window and ensure the three project links are visible.

**Do not** put unverified employer claims, personal email/phone placeholders, fabricated badges, or CI scores presented as production model quality on the profile.

## B. Publish the static one-page portfolio through GitHub Pages (optional)

Only a static HTML/CSS page is needed. It performs no API calls and uses no external dependencies.

1. Open [GuardEval's settings](https://github.com/reddydev-ai/guardeval/settings/pages).
2. Under **Build and deployment**, select **Deploy from a branch** (when available).
3. Select **`main`** and **`/docs`**, then **Save**.
4. Allow GitHub to report the Pages deployment URL. Do not assume a URL is live before checking it.
5. Open the published page and check mobile layout, keyboard navigation, external project links and the accuracy disclaimers.
6. Only after successful verification, link the exact published URL from the GitHub profile README and other project READMEs.

The current connected GitHub actions can modify repository files and PRs but do not provide reliable account/repository creation or Pages activation. These account-level steps **have not been performed**.

## C. Optional recruiter presentation checks

- [ ] Three source repositories visible on the public account
- [ ] About/description topics accurately reflect AI product management and technical scope
- [ ] Profile README displays prominently, when the profile repository has been created
- [ ] Repositories pinned in the desired order, if the account UI supports it
- [ ] Portfolio website published only after reviewing accessibility, wording and link behavior
- [ ] No real data or secrets in static assets
- [ ] README claims correspond to CI evidence and clearly identify unmeasured metrics

There is no need to publicly deploy PolicyMind or FlowAgent APIs to complete this presentation.

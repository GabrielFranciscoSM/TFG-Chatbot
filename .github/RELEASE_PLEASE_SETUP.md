# Release Please Configuration

## ⚠️ Setup Required

Release Please workflow requires additional permissions to create Pull Requests.

### Option 1: Configure Workflow Permissions (Easiest)

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Actions** → **General**
3. Scroll to **Workflow permissions**
4. Select: **"Read and write permissions"**
5. ✅ Check: **"Allow GitHub Actions to create and approve pull requests"**
6. Click **Save**

This allows the default `GITHUB_TOKEN` to create PRs.

### Option 2: Use Personal Access Token (More Secure)

If you prefer more control or option 1 doesn't work:

1. **Create a Personal Access Token (Classic)**
   - Go to GitHub → Settings (your profile) → Developer settings
   - Personal access tokens → Tokens (classic) → Generate new token
   - Name: `Release Please Token`
   - Expiration: Choose duration (recommend: 1 year)
   - Select scopes:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
   - Click **Generate token**
   - **Copy the token** (you won't see it again!)

2. **Add Token to Repository Secrets**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click **New repository secret**
   - Name: `RELEASE_PLEASE_TOKEN`
   - Value: Paste the token you copied
   - Click **Add secret**

3. **Verify Workflow**
   - The workflow automatically uses `RELEASE_PLEASE_TOKEN` if available
   - Falls back to `GITHUB_TOKEN` if not

### Verification

After configuration, test by pushing to main:

```bash
git commit --allow-empty -m "chore: test release please"
git push origin main
```

Check Actions tab - you should see Release Please create a PR.

## Workflow Behavior

### When It Runs
- Automatically on every push to `main`
- Manually via workflow_dispatch

### What It Does

1. **Analyzes commits** since last release using conventional commits:
   - `feat:` → Minor version bump (0.x.0)
   - `fix:` → Patch version bump (0.0.x)
   - `feat!:` or `BREAKING CHANGE:` → Major version bump (x.0.0)

2. **Creates/Updates Release PR** with:
   - Version bump in `pyproject.toml`
   - Updated `CHANGELOG.md`
   - Grouped commits by type

3. **When PR is merged** → Automatically:
   - Creates git tag
   - Creates GitHub Release
   - Builds Docker images
   - Publishes to GHCR

### Commit Message Format

```bash
# Features (minor bump: 0.1.0 → 0.2.0)
git commit -m "feat(backend): add new endpoint"
git commit -m "feat(rag): implement caching"

# Fixes (patch bump: 0.1.0 → 0.1.1)
git commit -m "fix(api): resolve timeout issue"
git commit -m "fix(docker): correct port mapping"

# Breaking changes (major bump: 0.1.0 → 1.0.0)
git commit -m "feat!: redesign API"
git commit -m "feat: new feature

BREAKING CHANGE: removed old endpoint"

# Non-release commits (no version change)
git commit -m "chore: update docs"
git commit -m "ci: fix workflow"
git commit -m "docs: improve README"
```

## Troubleshooting

### Error: "GitHub Actions is not permitted to create or approve pull requests"

**Solution**: Follow Option 1 above to enable PR creation permissions.

### Error: "Resource not accessible by integration"

**Solutions**:
1. Check workflow permissions (Option 1)
2. Use PAT instead (Option 2)
3. Verify repository is not archived/locked

### No Release PR Created

**Possible reasons**:
1. No releasable commits since last release
   - Need at least one `feat:` or `fix:` commit
   - `chore:`, `docs:`, `ci:` don't trigger releases

2. Commits don't follow conventional format
   - Check commit messages match the format above

3. Already have an open Release PR
   - Release Please updates existing PR instead of creating new one

### Want to Skip a Commit

Use `chore:` instead of `feat:` or `fix:`:
```bash
git commit -m "chore: update dependency (no release)"
```

### Force a Specific Version

You can't with Release Please - it calculates version automatically.
Use **Manual Release** workflow instead for full control.

## Comparison: Release Please vs Manual Release

| Feature | Release Please | Manual Release |
|---------|----------------|----------------|
| **Trigger** | Auto on main push | Manual button |
| **Version control** | Automatic from commits | You choose type |
| **PR preview** | Yes (before release) | No (direct release) |
| **Custom notes** | From commits only | Can add custom text |
| **Pre-releases** | No | Yes |
| **Control** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Ease of use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Best for** | CD pipeline | Controlled releases |

## Recommendation

**For this project**, use **Manual Release** if:
- You want control over release timing
- You need pre-release versions
- You want to add custom release notes
- Team is not strict about conventional commits

**Use Release Please** if:
- Team consistently uses conventional commits
- You want automated releases on every main merge
- You prefer continuous delivery approach
- You like reviewing release PR before publishing

---

**Default recommendation**: Start with **Manual Release** workflow, switch to Release Please later if needed.

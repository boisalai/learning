# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-29

### Added
- New `SchoolSuppliesSupplement` calculator module for Quebec's school supplies benefit
  - Fixed amount per child (121$ in 2024)
  - Eligibility based on child's age (4-16 years as of September 30)
  - Support for shared custody situations
  - Visualization tools and test cases included

### Changed
- Separated school supplies calculation from Family Allowance
- Updated `FamilyAllowance` to focus solely on base allowance and disability supplements
- Modified `PythonTaxCalculator` to handle school supplies as a separate component
- Improved readability and maintainability of the codebase through modular design

### Fixed
- More accurate calculation of school supplies benefit by dedicated handling
- Clearer separation of concerns between different types of family benefits

## [1.0.0] - 2024-12-28

### Added
- Initial release of the tax calculator
- Support for Quebec and Federal tax calculations
- Basic family benefits and credits
- Contribution calculations

[1.1.0]: https://github.com/boisalai/learning/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/boisalai/learning/releases/tag/v1.0.0
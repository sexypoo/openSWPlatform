
<br/>
<br/>

## 💡 기술 블로그 바로가기 💡

<a href="https://2025osp-group5.tistory.com/2">[개념] UI는 어떻게 서버 데이터와 연결될까? FE-BE 연결 구조를 중심으로</a>

<a href="https://2025osp-group5.tistory.com/3">[디버깅] 다중 이미지 업로드와 슬라이드 디버깅</a>

<a href="https://2025osp-group5.tistory.com/4">[가이드] GitHub Desktop 설치와 사용법 (Feat. PyCharm)</a>

<a href="https://2025osp-group5.tistory.com/5">[해설] CSS Grid와 Jinja2로 깔끔한 '리뷰 목록' UI 개발하기</a>

<a href="https://2025osp-group5.tistory.com/6">[해설] 간단하지만 위험한 백엔드는 그만! 백엔드 시큐어 코딩 적용기</a>

<br/>
<br/>

# 0. Getting Started (시작하기)
### Firebase 설정
`authenticatin/firebase_auth.json` 추가

### 실행
```bash
$ python app.py
```

<br/>
<br/>

# 1. Project Overview (프로젝트 개요)
- 프로젝트 이름: Ewha Market
- 프로젝트 설명: 이화여대 학생들의 편리하고 안전한 중고거래 플랫폼

<br/>
<br/>

# 2. Team Members (팀원 및 팀 소개)
| 박고은 | 이민경 | 김은규 | 오서현 | 채서윤 |
|:------:|:------:|:------:|:------:|:------:|
| <img src="https://avatars.githubusercontent.com/u/60212998?v=4" alt="박고은" width="150"> | <img src="https://avatars.githubusercontent.com/u/162548821?v=4" alt="이민경" width="150"> | <img src="https://avatars.githubusercontent.com/u/228705566?v=4" alt="김은규" width="150"> | <img src="https://avatars.githubusercontent.com/u/229738206?v=4" alt="오서현" width="150"> | <img src="https://avatars.githubusercontent.com/u/231133650?v=4" alt="채서윤" width="150"> |
| PL(BE) | BE | FE | FE | FE |
| [GitHub](https://github.com/sexypoo) | [GitHub](https://github.com/emilyminkyounglee) | [GitHub](https://github.com/angmang24-commits) | [GitHub](https://github.com/sooupyy3-lang) | [GitHub](https://github.com/chaeuniv) |

<br/>
<br/>

# 3. Key Features (주요 기능)
- **회원가입**:
  - 회원가입 시 DB에 유저정보가 등록됩니다.

- **로그인**:
  - 사용자 인증 정보를 통해 로그인합니다.

- **상품 등록**:
  - 판매하고 싶은 상품의 정보를 등록합니다.
  - 이미지를 총 3개까지 등록할 수 있습니다.

- **상품 조회**:
  - 유저들이 올린 상품을 조회할 수 있습니다.
  - 태그/카테고리 별 필터링이 가능합니다.
  - 세부 조회에서 상품 구매/리뷰 작성이 가능합니다.

- **리뷰 작성**:
  - 유저들이 올린 상품의 리뷰를 작성할 수 있습니다.
  - 상품을 통해 리뷰를 작성할 수도 있고, 개별 리뷰를 올릴 수도 있습니다.
  - 이미지를 총 3개까지 등록할 수 있습니다.

- **리뷰 조회**:
  - 유저들이 올린 리뷰를 조회할 수 있습니다.

- **마이페이지**:
  - 마이페이지에서 회원정보를 수정할 수 있습니다.
  - 판매 내역, 구매 내역, 위시리스트 목록 등을 보고 관리할 수 있습니다.

<br/>
<br/>

# 4. Tasks & Responsibilities (작업 및 역할 분담)
|  |  |  |
|-----------------|-----------------|-----------------|
| 박고은    |  <img src="https://avatars.githubusercontent.com/u/60212998?v=4" alt="박고은" width="100"> | <ul><li>프로젝트 계획 및 관리</li><li>팀 리딩 및 커뮤니케이션</li><li>리뷰 CURD 개발</li><li>마이페이지 기능 개발</li><li>기타 BE 개발</li></ul>     |
| 이민경   |  <img src="https://avatars.githubusercontent.com/u/162548821?v=4" alt="이민경" width="100">| <ul><li>상품 CRUD 개발</li><li>로그인/회원가입 개발</li><li>기타 BE 개발</li></ul> |
| 김은규   |  <img src="https://avatars.githubusercontent.com/u/228705566?v=4" alt="김은규" width="100">    |<ul><li>상품 등록 페이지 개발</li><li>상품 전체 조회 페이지 개발</li><li>상품 상세 조회 페이지 개발</li><li>기타 FE 개발</li></ul>  |
| 오서현    |  <img src="https://avatars.githubusercontent.com/u/229738206?v=4" alt="오서현" width="100">    | <ul><li>리뷰 등록 페이지 개발</li><li>리뷰 전체 조회 페이지 개발</li><li>리뷰 상세 조회 페이지 개발</li><li>기타 FE 개발</li></ul>    |
| 채서윤    |  <img src="https://avatars.githubusercontent.com/u/231133650?v=4" alt="채서윤" width="100">    | <ul><li>회원가입 페이지 개발</li><li>로그인 페이지 개발</li><li>마이페이지 개발</li><li>메인페이지 개발</li><li>기타 FE 개발</li></ul>    |

<br/>
<br/>

# 5. Technology Stack (기술 스택)
## 5.1 Frontend
|  |  |
|-----------------|-----------------|
| HTML5    |<img src="https://github.com/user-attachments/assets/2e122e74-a28b-4ce7-aff6-382959216d31" alt="HTML5" width="100">| 
| CSS3    |   <img src="https://github.com/user-attachments/assets/c531b03d-55a3-40bf-9195-9ff8c4688f13" alt="CSS3" width="100">|
| Javascript    |  <img src="https://github.com/user-attachments/assets/4a7d7074-8c71-48b4-8652-7431477669d1" alt="Javascript" width="100"> | 

<br/>

## 5.2 Backend
|  |  |  
|-----------------|-----------------|
| Flask    |  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Flask_logo.svg/640px-Flask_logo.svg.png" alt="Flask" width="100">    |
| Firebase    |  <img src="https://github.com/user-attachments/assets/1694e458-9bb0-4a0b-8fe6-8efc6e675fa1" alt="Firebase" width="100">    |

<br/>

## 5.3 Cooperation
|  |  |
|-----------------|-----------------|
| Git    |  <img src="https://github.com/user-attachments/assets/483abc38-ed4d-487c-b43a-3963b33430e6" alt="git" width="100">    |
| Notion    |  <img src="https://github.com/user-attachments/assets/34141eb9-deca-416a-a83f-ff9543cc2f9a" alt="Notion" width="100">    |

<br/>

# 6. Project Structure (프로젝트 구조)
## 프로젝트 구조

```text
openSWPlatform/
├── LICENSE
├── README.md
├── backend
│   ├── ProductForm.py
│   ├── ReviewForm.py
│   ├── __init__.py # 블루프린트 설정
│   ├── auth.py # 회원가입, 로그인 인증 기능
│   ├── pages.py # page 라우팅
│   ├── products.py # 상품 관련 기능
│   ├── reviews.py # 리뷰 관련 기능
│   ├── user.py # 마이페이지 관련 기능
│   └── wish.py # 위시리스트 기능
├── app.py
├── authentication
│   └── firebase_auth.json
├── database.py # DB Handler
├── static
│   ├── css
│   │   ├── common_style.css # 공통 스타일
│   │   ├── product_style.css # 상품 관련 스타일
│   │   ├── review_style.css # 리뷰 관련 스타일
│   │   └── userhome_style.css # 마이페이지 관련 스타일
│   ├── main.js # 공통 js
│   └── mypage_common.js # 마이페이지 공통 js
└── templates
    ├── edit_product.html
    ├── index.html
    ├── layout.html
    ├── login.html
    ├── mypage
    │   ├── _buyList.html
    │   ├── _myreview.html
    │   ├── _profile.html
    │   ├── _sellList.html
    │   └── _wishlist.html
    ├── mypage.html
    ├── product_detail.html
    ├── products.html
    ├── reg_product.html
    ├── reg_reviews.html
    ├── review.html
    ├── review_detail.html
    ├── signup.html
    └── wishlist.html
```

<br/>
<br/>

# 7. Development Workflow (개발 워크플로우)
## 브랜치 전략 (Branch Strategy)
우리의 브랜치 전략은 Git Flow를 기반으로 하며, 다음과 같은 브랜치를 사용합니다.

- Main Branch
  - 배포 가능한 상태의 코드를 유지합니다.
  - 모든 배포는 이 브랜치에서 이루어집니다.
  
- {name} Branch
  - 팀원 각자의 개발 브랜치입니다.
  - 모든 기능 개발은 이 브랜치에서 이루어집니다.

<br/>
<br/>

# 8. 커밋 컨벤션
## 기본 구조
```
type : subject

body 
```

<br/>

## type 종류
```
feat : 새로운 기능 추가
fix : 버그 수정
docs : 문서 수정
style : 코드 포맷팅, 코드 변경이 없는 경우
refactor : 코드 리펙토링
```

<br/>

## 커밋 예시
```
== ex1
✨Feat: "회원 가입 기능 구현"

아이디 중복확인 기능 개발

== ex2
📚refactor: product 관련 변수 이름 통일

items와 products 변수 혼용 통일
```

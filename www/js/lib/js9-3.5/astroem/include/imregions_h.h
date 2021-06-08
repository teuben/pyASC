static char *IMREGIONS_H="\n#if MINIMIZE_INCLUDES\n\n#include <stdarg.h>\nint sscanf(const char *s, const char *format, ...);\ntypedef unsigned long size_t;\nsize_t strlen();\nchar *strcpy(), *strdup(), *strstr(), *getenv();\nvoid *calloc(), *malloc(), *memset(), *memmove();\nvoid exit();\n\n\nextern double  acos(double);\nextern double  asin(double);\nextern double  atan(double);\nextern double  atan2(double, double);\nextern double  cos(double);\nextern double  sin(double);\nextern double  tan(double);\nextern double  acosh(double);\nextern double  asinh(double);\nextern double  atanh(double);\nextern double  cosh(double);\nextern double  sinh(double);\nextern double  tanh(double);\nextern double exp (double);\nextern double exp2 (double); \nextern double expm1 (double); \nextern double log (double);\nextern double log10 (double);\nextern double log2 (double);\nextern double log1p (double);\nextern double logb (double);\nextern double modf (double, double *);\nextern double ldexp (double, int);\nextern double frexp (double, int *);\nextern int ilogb (double);\nextern double scalbn (double, int);\nextern double scalbln (double, long int);\nextern double  fabs(double);\nextern double  cbrt(double);\nextern double hypot (double, double);\nextern double pow (double, double);\nextern double  sqrt(double);\nextern double  erf(double);\nextern double  erfc(double);\nextern double  lgamma(double);\nextern double  tgamma(double);\nextern double ceil (double);\nextern double floor (double);\nextern double nearbyint (double);\nextern double rint (double);\nextern long int lrint (double);\nextern double round (double);\nextern long int lround (double);\nextern double trunc (double);\nextern double fmod (double, double);\nextern double remainder (double, double);\nextern double remquo (double, double, int *);\nextern double copysign (double, double);\nextern double nan(const char *);\nextern double nextafter (double, double);\nextern double fdim (double, double);\nextern double fmax (double, double);\nextern double fmin (double, double);\nextern double fma (double, double, double);\n\n#define M_E         2.71828182845904523536028747135266250   \n#define M_LOG2E     1.44269504088896340735992468100189214   \n#define M_LOG10E    0.434294481903251827651128918916605082  \n#define M_LN2       0.693147180559945309417232121458176568  \n#define M_LN10      2.30258509299404568401799145468436421   \n#define M_PI        3.14159265358979323846264338327950288   \n#define M_PI_2      1.57079632679489661923132169163975144   \n#define M_PI_4      0.785398163397448309615660845819875721  \n#define M_1_PI      0.318309886183790671537767526745028724  \n#define M_2_PI      0.636619772367581343075535053490057448  \n#define M_2_SQRTPI  1.12837916709551257389615890312154517   \n#define M_SQRT2     1.41421356237309504880168872420969808   \n#define M_SQRT1_2   0.707106781186547524400844362104849039  \n\n#else \n\n#include <stdio.h>\n#include <unistd.h>\n#include <math.h>\n#include <string.h>\n#include <sys/types.h>\n#ifdef __STDC__\n#include <stdlib.h>\n#include <stdarg.h>\n#else\n#include <varargs.h>\n#endif\n\n#endif \n\n\n\n#define TOK_EREG	1\n#define TOK_NREG	2\n#define TOK_IREG	4\n#define TOK_RTINE	8\n#define TOK_NAME	16\n#define TOK_ACCEL	32\n#define TOK_VARARGS	64\n#define TOK_REG		(TOK_EREG|TOK_NREG|TOK_IREG)\n\n\n\n#ifndef	__regions_h\n\n\n\ntypedef struct regmasks {\n  int region;\n  int y;\n  int xstart, xstop;\n} *RegionsMask, RegionsMaskRec;\n\n\n#endif\n\n\ntypedef struct scanrec{\n  struct scanrec *next;\n  int x;\n} *Scan, ScanRec;\n\n\ntypedef struct shaperec {\n  int init;\n  double ystart, ystop;\n  Scan *scanlist;\n  \n  int nv;\n  double *xv;\n  \n  double r1sq, r2sq;\n  \n  double angl, sinangl, cosangl;\n  double cossq, sinsq;\n  double xradsq, yradsq;\n  double a;\n  \n  int npt;\n  double *pts;\n  \n  int xonly;\n  double x1, x2, y1;\n  double invslope;\n} *Shape, ShapeRec;\n\n\ntypedef struct gregrec {\n  int nshape;			\n  int maxshape;			\n  Shape shapes;			\n  int rid;			\n  int xmin, xmax, ymin, ymax;	\n  int block;			\n  int x0, x1, y0, y1;		\n  int *ybuf;			\n  int *x0s;			\n  int *x1s;			\n} *GReg, GRegRec;\n\n#ifndef M_PI\n#define M_PI		3.14159265358979323846\n#endif\n#define SMALL_NUMBER	1.0E-24\n#define LARGE_NUMBER	65535\n\n\n#define PSTOP		9007199254740992.0\n\n#ifndef SZ_LINE\n#define SZ_LINE 	4096\n#endif\n#ifndef min\n#define min(x,y)	(((x)<(y))?(x):(y))\n#endif\n#ifndef max\n#define max(x,y)	(((x)>(y))?(x):(y))\n#endif\n#ifndef abs\n#define abs(x)		((x)<0?(-x):(x))\n#endif\n#ifndef feq\n#define feq(x,y)	(fabs((double)x-(double)y)<=(double)1.0E-15)\n#endif\n#ifndef NULL\n#define NULL 		(void *)0\n#endif\n\n#define PIXCEN(a)	(double)(a)\n#define PIXNUM(a)	(int)((a)+0.5) \n#define PIXSTART(a)	((int)(a)+1)\n#define PIXSTOP(a)	(((int)(a))==(a)?((int)(a)-1):((int)(a)))\n\n\n\n#define PIXINCL(a)	(int)((a)+1.0) \n\n#define XSNO    3\n\n\nvoid imannulusi(GReg g, int rno, int sno, int flag, int type, \n		double x, double y,\n		double xcen, double ycen, double iradius, double oradius);\nvoid imboxi(GReg g, int rno, int sno, int flag, int type,\n	    double x, double y,\n	    double xcen, double ycen, double xwidth, double yheight,\n	    double angle);\nvoid imcirclei(GReg g, int rno, int sno, int flag, int type,\n	       double x, double y,\n	       double xcen, double ycen, double radius);\nvoid imellipsei(GReg g, int rno, int sno, int flag, int type,\n		double x, double y,\n		double xcen, double ycen, double xrad, double yrad,\n		double angle);\nvoid imfieldi(GReg g, int rno, int sno, int flag, int type,\n	      double x, double y);\nvoid imlinei(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y,\n	     double x0, double y0, double x1, double y1);\nvoid impiei(GReg g, int rno, int sno, int flag,  int type,\n	    double x, double y,\n	    double xcen, double ycen, double angle1, double angle2);\nvoid imqtpiei(GReg g, int rno, int sno, int flag,  int type,\n	      double x, double y,\n	      double xcen, double ycen, double angle1, double angle2);\nvoid impointi(GReg g, int rno, int sno, int flag, int type,\n	      double x, double y,\n	      double xcen, double ycen);\nvoid impandai(GReg g, int rno, int sno, int flag, int type,\n	      double x, double y,\n	      double xcen, double ycen,\n	      double anglo, double anghi, double angn,\n	      double radlo, double radhi, double radn);\nvoid imbpandai(GReg g, int rno, int sno, int flag, int type,\n	       double x, double y,\n	       double xcen, double ycen,\n	       double anglo, double anghi, double angn,\n	       double xlo, double ylo, double xhi, double yhi, double radn,\n	       double ang);\nvoid imepandai(GReg g, int rno, int sno, int flag, int type,\n	       double x, double y,\n	       double xcen, double ycen,\n	       double anglo, double anghi, double angn,\n	       double xlo, double ylo, double xhi, double yhi, double radn,\n	       double ang);\nvoid imnannulusi(GReg g, int rno, int sno, int flag, int type,\n		 double x, double y,\n		 double xcen, double ycen,\n		 double lo, double hi, int n);\nvoid imnboxi(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y,\n	     double xcen, double ycen,\n	     double lox, double loy, double hix, double hiy, int n,\n	     double angle);\nvoid imnellipsei(GReg g, int rno, int sno, int flag, int type,\n		 double x, double y,\n		 double xcen, double ycen,\n		 double lox, double loy, double hix, double hiy, int n,\n		 double angle);\nvoid imnpiei(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y,\n	     double xcen, double ycen,\n	     double lo, double hi, int n);\n\n#ifdef __STDC__\nvoid impolygoni(GReg g, int rno, int sno, int flag, int type,\n		double x, double y, ...);\nvoid imvannulusi(GReg g, int rno, int sno, int flag, int type,\n		 double x, double y, double xcen, double ycen, ...);\nvoid imvboxi(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y, double xcen, double ycen, ...);\nvoid imvellipsei(GReg g, int rno, int sno, int flag, int type,\n		 double x, double y, double xcen, double ycen, ...);\nvoid imvpiei(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y, double xcen, double ycen, ...);\nvoid imvpointi(GReg g, int rno, int sno, int flag, int type, \n	       double x, double y, ...);\n#endif\n\n\n\nint imannulus(GReg g, int rno, int sno, int flag, int type,\n	      double x, double y,\n	      double xcen, double ycen, double iradius, double oradius);\nint imbox(GReg g, int rno, int sno, int flag, int type,\n	  double x, double y,\n	  double xcen, double ycen, double xwidth, double yheight,\n	  double angle);\nint imcircle(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y,\n	     double xcen, double ycen, double radius);\nint imellipse(GReg g, int rno, int sno, int flag, int type,\n	      double x, double y,\n	      double xcen, double ycen, double xrad, double yrad,\n	      double angle);\nint imfield(GReg g, int rno, int sno, int flag, int type,\n	    double x, double y);\nint imline(GReg g, int rno, int sno, int flag, int type,\n	   double x, double y,\n	   double x1, double y1, double x2, double y2);\nint impie(GReg g, int rno, int sno, int flag, int type,\n	  double x, double y,\n	  double xcen, double ycen, double angle1, double angle2);\nint imqtpie(GReg g, int rno, int sno, int flag, int type,\n	    double x, double y,\n	    double xcen, double ycen, double angle1, double angle2);\nint impoint(GReg g, int rno, int sno, int flag, int type,\n	    double x, double y,\n	    double xcen, double ycen);\nint impanda(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y,\n	     double xcen, double ycen,\n	     double anglo, double anghi, double angn,\n	     double radlo, double radhi, double radn);\nint imbpanda(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y,\n	     double xcen, double ycen,\n	     double anglo, double anghi, double angn,\n	     double xlo, double ylo, double xhi, double yhi, double radn,\n	     double ang);\nint imepanda(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y,\n	     double xcen, double ycen,\n	     double anglo, double anghi, double angn,\n	     double xlo, double ylo, double xhi, double yhi, double radn,\n	     double ang);\nint imnannulus(GReg g, int rno, int sno, int flag, int type,\n	       double x, double y,\n	       double xcen, double ycen,\n	       double lo, double hi, int n);\nint imnbox(GReg g, int rno, int sno, int flag, int type,\n	   double x, double y,\n	   double xcen, double ycen,\n	   double lox, double loy, double hix, double hiy, int n,\n	   double angle);\nint imnellipse(GReg g, int rno, int sno, int flag, int type,\n	       double x, double y,\n	       double xcen, double ycen,\n	       double lox, double loy, double hix, double hiy, int n,\n	       double angle);\nint imnpie(GReg g, int rno, int sno, int flag, int type,\n	   double x, double y,\n	   double xcen, double ycen,\n	   double lo, double hi, int n);\n#ifdef __STDC__\nint impolygon(GReg g, int rno, int sno, int flag, int type,\n	      double x, double y, ...);\nint imvannulus(GReg g, int rno, int sno, int flag, int type,\n	       double x, double y, double xcen, double ycen, ...);\nint imvbox(GReg g, int rno, int sno, int flag, int type,\n	   double x, double y, double xcen, double ycen, ...);\nint imvellipse(GReg g, int rno, int sno, int flag, int type,\n	       double x, double y, double xcen, double ycen, ...);\nint imvpie(GReg g, int rno, int sno, int flag, int type,\n	   double x, double y, double xcen, double ycen, ...);\nint imvpoint(GReg g, int rno, int sno, int flag, int type,\n	     double x, double y, ...);\n#endif\n";

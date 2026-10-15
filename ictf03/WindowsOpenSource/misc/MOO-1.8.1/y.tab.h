#ifndef BISON_Y_TAB_H
# define BISON_Y_TAB_H

#ifndef YYSTYPE
typedef union {
  Stmt	       *stmt;
  Expr	       *expr;
  int		integer;
  Objid		object;
  double       *real;
  char	       *string;
  enum error	error;
  Arg_List     *args;
  Cond_Arm     *arm;
  Except_Arm   *except;
  Scatter      *scatter;
} yystype;
# define YYSTYPE yystype
# define YYSTYPE_IS_TRIVIAL 1
#endif
# define	tINTEGER	257
# define	tOBJECT	258
# define	tFLOAT	259
# define	tSTRING	260
# define	tID	261
# define	tERROR	262
# define	tIF	263
# define	tELSE	264
# define	tELSEIF	265
# define	tENDIF	266
# define	tFOR	267
# define	tIN	268
# define	tENDFOR	269
# define	tRETURN	270
# define	tFORK	271
# define	tENDFORK	272
# define	tWHILE	273
# define	tENDWHILE	274
# define	tTRY	275
# define	tENDTRY	276
# define	tEXCEPT	277
# define	tFINALLY	278
# define	tANY	279
# define	tBREAK	280
# define	tCONTINUE	281
# define	tTO	282
# define	tARROW	283
# define	tOR	284
# define	tAND	285
# define	tEQ	286
# define	tNE	287
# define	tLE	288
# define	tGE	289
# define	tUNARYMINUS	290


extern YYSTYPE yylval;

#endif /* not BISON_Y_TAB_H */

FROM mswebench/catchorg_m_catch2:base-cpp-7



COPY fix.patch /home/
COPY test.patch /home/
COPY check_git_changes.sh /home/
COPY prepare.sh /home/
COPY run.sh /home/
COPY test-run.sh /home/
COPY fix-run.sh /home/


RUN bash /home/prepare.sh



